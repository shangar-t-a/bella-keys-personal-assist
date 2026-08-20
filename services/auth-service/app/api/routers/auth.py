"""API Router for Authentication endpoints."""

from datetime import UTC, datetime, timedelta
import uuid

from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
from jose import (
    JWTError,
    jwt,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import get_settings
from app.core.constants import (
    ALGORITHM_HS256,
    COOKIE_REFRESH_TOKEN,
    SECONDS_PER_MINUTE,
    TOKEN_TYPE_BEARER,
    TOKEN_TYPE_BEARER_LOWER,
)
from app.core.cookies import (
    delete_refresh_token_cookie,
    set_refresh_token_cookie,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.db.database import get_db
from app.db.models import (
    RefreshToken,
    User,
)
from app.schemas.auth import (
    Token,
    UserCreate,
    UserResponse,
)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    """Dependency to get the current authenticated user via JWT access token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": TOKEN_TYPE_BEARER},
    )
    try:
        secret = get_settings().JWT_SECRET.get_secret_value()
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM_HS256])
        username: str | None = payload.get("sub")
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


@router.post("/login", response_model=Token, deprecated=True)
async def login(
    response: Response,
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """[DEPRECATED] Authenticate user credentials and return access token.

    Warning: This endpoint is legacy/deprecated. Use the OAuth 2.1 authorization
    redirection flow (/oauth/authorize) with PKCE instead.
    """
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": TOKEN_TYPE_BEARER},
        )

    user.last_login = datetime.now(UTC).replace(tzinfo=None)
    await db.commit()

    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    refresh_token = create_refresh_token(data={"sub": user.username, "role": user.role})

    new_rt = RefreshToken(
        token=refresh_token,
        user_id=user.id,
        expires_at=datetime.now(UTC).replace(tzinfo=None) + timedelta(days=get_settings().REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(new_rt)
    await db.commit()

    secure_flag = request.url.scheme == "https"
    set_refresh_token_cookie(response, refresh_token, secure_flag)

    return {
        "access_token": access_token,
        "token_type": TOKEN_TYPE_BEARER_LOWER,
        "expires_in": get_settings().ACCESS_TOKEN_EXPIRE_MINUTES * SECONDS_PER_MINUTE,
    }


@router.post("/refresh", response_model=Token)
async def refresh(
    response: Response,
    request: Request,
    refresh_token: str | None = Cookie(default=None, alias=COOKIE_REFRESH_TOKEN),
    db: AsyncSession = Depends(get_db),
):
    """Issue a new access token using a valid refresh token cookie."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": TOKEN_TYPE_BEARER},
    )

    if not refresh_token:
        raise credentials_exception

    try:
        secret = get_settings().JWT_SECRET.get_secret_value()
        payload = jwt.decode(refresh_token, secret, algorithms=[ALGORITHM_HS256])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception from None

    result = await db.execute(select(RefreshToken).where(RefreshToken.token == refresh_token))
    rt_record = result.scalars().first()

    now_naive = datetime.now(UTC).replace(tzinfo=None)
    if not rt_record or rt_record.expires_at < now_naive:
        raise credentials_exception

    result_user = await db.execute(select(User).where(User.id == rt_record.user_id))
    user = result_user.scalars().first()
    if not user:
        raise credentials_exception

    rt_client_id = payload.get("client_id")
    rt_scope = payload.get("scope")
    rt_aud = payload.get("aud") or get_settings().DEFAULT_RESOURCE_AUDIENCE

    access_token_data = {
        "iss": f"{request.url.scheme}://{request.url.netloc}",
        "sub": user.username,
        "aud": rt_aud,
        "client_id": rt_client_id,
        "iat": datetime.now(UTC),
        "nbf": datetime.now(UTC),
        "jti": uuid.uuid4().hex,
        "scope": rt_scope or "",
        "role": user.role,
    }
    access_token = create_access_token(data=access_token_data)

    new_rt_data = {
        "sub": user.username,
        "role": user.role,
        "client_id": rt_client_id,
        "scope": rt_scope or "",
        "aud": rt_aud,
    }
    new_refresh_token = create_refresh_token(data=new_rt_data)

    expires_days = get_settings().REFRESH_TOKEN_EXPIRE_DAYS
    rt_record.expires_at = datetime.now(UTC).replace(tzinfo=None) + timedelta(days=expires_days)
    await db.commit()

    secure_flag = request.url.scheme == "https"
    set_refresh_token_cookie(response, new_refresh_token, secure_flag)

    return {
        "access_token": access_token,
        "token_type": TOKEN_TYPE_BEARER_LOWER,
        "expires_in": get_settings().ACCESS_TOKEN_EXPIRE_MINUTES * SECONDS_PER_MINUTE,
    }


@router.post("/logout")
async def logout(response: Response):
    """Clear the refresh token cookie to log out the user."""
    delete_refresh_token_cookie(response)
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Fetch the currently authenticated user's profile."""
    return UserResponse(id=str(current_user.id), username=current_user.username, role=current_user.role)
