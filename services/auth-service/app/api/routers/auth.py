"""API Router for Authentication endpoints."""

from datetime import datetime, timedelta

from fastapi import (APIRouter,
    Depends,
    HTTPException,
    status,
    Response,
    Request,
    Cookie
)
from fastapi.security import (OAuth2PasswordBearer,
    OAuth2PasswordRequestForm
)
from jose import (JWTError,
    jwt
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import get_settings
from app.core.security import (ALGORITHM,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password
)
from app.db.database import get_db
from app.db.models import (RefreshToken,
    User
)
from app.schemas.auth import (RefreshRequest,
    Token,
    UserCreate,
    UserResponse
)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    """Dependency to get the current authenticated user via JWT access token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        secret = get_settings().JWT_SECRET.get_secret_value()
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception from None

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    return user


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user in the system."""
    result = await db.execute(select(User).where(User.username == user_in.username))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = get_password_hash(user_in.password)
    new_user = User(username=user_in.username, password_hash=hashed_password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"message": "User created successfully."}


@router.post("/login", response_model=Token)
async def login(
    response: Response,
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user credentials and return dual tokens."""
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user.last_login = datetime.utcnow()
    await db.commit()

    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    refresh_token = create_refresh_token(data={"sub": user.username, "role": user.role})

    # Store refresh token in DB
    new_rt = RefreshToken(
        token=refresh_token,
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=get_settings().REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(new_rt)
    await db.commit()

    # Set refresh token in HttpOnly cookie
    secure_flag = request.url.scheme == "https"
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=secure_flag,
        samesite="lax",
        path="/"
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": get_settings().ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/refresh", response_model=Token)
async def refresh(
    response: Response,
    request: Request,
    req: RefreshRequest | None = None,
    refresh_token_cookie: str | None = Cookie(default=None, alias="refresh_token"),
    db: AsyncSession = Depends(get_db)
):
    """Issue a new access token using a valid refresh token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Resolve refresh token from cookie or body
    token_to_use = refresh_token_cookie
    if not token_to_use and req and req.refresh_token:
        token_to_use = req.refresh_token

    if not token_to_use:
        raise credentials_exception

    try:
        secret = get_settings().JWT_SECRET.get_secret_value()
        payload = jwt.decode(token_to_use, secret, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception from None

    # Check if refresh token is in DB
    result = await db.execute(select(RefreshToken).where(RefreshToken.token == token_to_use))
    rt_record = result.scalars().first()

    if not rt_record or rt_record.expires_at < datetime.utcnow():
        raise credentials_exception

    result_user = await db.execute(select(User).where(User.id == rt_record.user_id))
    user = result_user.scalars().first()
    if not user:
        raise credentials_exception

    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    new_refresh_token = create_refresh_token(data={"sub": user.username, "role": user.role})

    # Rotate refresh token
    rt_record.token = new_refresh_token
    rt_record.expires_at = datetime.utcnow() + timedelta(days=get_settings().REFRESH_TOKEN_EXPIRE_DAYS)
    await db.commit()

    # Set rotated refresh token in HttpOnly cookie
    secure_flag = request.url.scheme == "https"
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=secure_flag,
        samesite="lax",
        path="/"
    )

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": get_settings().ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/logout")
async def logout(response: Response):
    """Clear the refresh token cookie to log out the user."""
    response.delete_cookie(key="refresh_token", path="/")
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Fetch the currently authenticated user's profile."""
    return UserResponse(id=str(current_user.id), username=current_user.username, role=current_user.role)
