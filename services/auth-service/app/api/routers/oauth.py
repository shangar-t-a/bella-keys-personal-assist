"""API Router for OAuth 2.1 endpoints."""

import contextlib
from datetime import datetime, UTC, timedelta
import os

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import get_settings
from app.core.oauth_clients import validate_client
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
)
from app.db.database import get_db
from app.db.models import User, RefreshToken
from app.schemas.oauth import (
    OAuthAuthorizeForm,
    OAuthAuthorizeParams,
)
from app.services.oauth import (
    create_authorization_code,
    prune_expired_codes,
    validate_and_consume_code,
)

router = APIRouter()

# Initialize templates folder relative to this file
TEMPLATES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates"
)
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("/.well-known/oauth-authorization-server")
@router.get("/.well-known/openid-configuration")
async def oauth_metadata(request: Request):
    """Serve metadata configuration for OAuth 2.1 / OIDC discovery."""
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    return {
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/oauth/authorize",
        "token_endpoint": f"{base_url}/oauth/token",
        "userinfo_endpoint": f"{base_url}/oauth/userinfo",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "code_challenge_methods_supported": ["S256"],
        "scopes_supported": ["openid", "profile", "email"],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": ["HS256"],
        "client_id_metadata_document_supported": True,
    }


@router.get("/oauth/authorize", response_class=HTMLResponse)
async def oauth_authorize_get(
    request: Request,
    params: OAuthAuthorizeParams = Depends(),
):
    """Render the OAuth 2.1 login and consent form."""
    # Strict validation of client ID and redirect URI
    validate_client(params.client_id, params.redirect_uri)

    client_name = (
        params.client_id.rsplit("/", 1)[-1]
        if "/" in params.client_id
        else params.client_id
    )
    if client_name.endswith(".json"):
        client_name = client_name[:-5]

    return templates.TemplateResponse(
        request=request,
        name="authorize.html",
        context={
            "client_name": client_name,
            "client_id": params.client_id,
            "redirect_uri": params.redirect_uri,
            "response_type": params.response_type,
            "code_challenge": params.code_challenge,
            "code_challenge_method": params.code_challenge_method,
            "state": params.state or "",
            "resource": params.resource or "",
            "scope": params.scope or "",
            "error_html": "",
        },
    )


@router.post("/oauth/authorize", response_class=HTMLResponse)
async def oauth_authorize_post(
    request: Request,
    response: Response,
    form: OAuthAuthorizeForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Authenticate credentials and redirect back with authorization code."""
    # Strict validation of client ID and redirect URI
    validate_client(form.client_id, form.redirect_uri)

    client_name = (
        form.client_id.rsplit("/", 1)[-1]
        if "/" in form.client_id
        else form.client_id
    )
    if client_name.endswith(".json"):
        client_name = client_name[:-5]

    result = await db.execute(
        select(User).where(User.username == form.username)
    )
    user = result.scalars().first()

    if not user or not verify_password(form.password, user.password_hash):
        error_msg = "Incorrect username or password"
        return templates.TemplateResponse(
            request=request,
            name="authorize.html",
            context={
                "client_name": client_name,
                "client_id": form.client_id,
                "redirect_uri": form.redirect_uri,
                "response_type": form.response_type,
                "code_challenge": form.code_challenge,
                "code_challenge_method": form.code_challenge_method,
                "state": form.state or "",
                "resource": form.resource or "",
                "scope": form.scope or "",
                "error_html": error_msg,
            },
            status_code=401,
        )

    # Evict expired authorization codes to prevent database bloat
    await prune_expired_codes(db)

    # Generate and persist temporary authorization code in DB
    code = await create_authorization_code(
        db=db,
        client_id=form.client_id,
        redirect_uri=form.redirect_uri,
        code_challenge=form.code_challenge,
        code_challenge_method=form.code_challenge_method,
        username=form.username,
        role=user.role,
        resource=form.resource,
        scope=form.scope,
    )

    # Generate refresh token to establish session (for React/Electron silent refresh compatibility)
    refresh_token = create_refresh_token(data={"sub": user.username, "role": user.role})
    new_rt = RefreshToken(
        token=refresh_token,
        user_id=user.id,
        expires_at=datetime.now(UTC).replace(tzinfo=None) + timedelta(days=get_settings().REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(new_rt)
    await db.commit()

    redirect_url = f"{form.redirect_uri}?code={code}"
    if form.state:
        redirect_url += f"&state={form.state}"

    # Use 303 Redirect so the browser redirects using GET request
    redirect_response = RedirectResponse(url=redirect_url, status_code=303)

    # Set refresh token in HttpOnly cookie on client response
    secure_flag = request.url.scheme == "https"
    redirect_response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=secure_flag,
        samesite="lax",
        path="/"
    )

    return redirect_response


@router.post("/oauth/token")
async def oauth_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Exchange authorization code for JWT access token with target resource indicator binding."""
    await prune_expired_codes(db)

    # Attempt to handle both form-urlencoded and JSON bodies
    form_data = {}
    with contextlib.suppress(Exception):
        form_data = await request.form()

    json_data = {}
    with contextlib.suppress(Exception):
        json_data = await request.json()

    grant_type = form_data.get("grant_type") or json_data.get("grant_type")
    code = form_data.get("code") or json_data.get("code")
    client_id = form_data.get("client_id") or json_data.get("client_id")
    redirect_uri = (
        form_data.get("redirect_uri") or json_data.get("redirect_uri")
    )
    code_verifier = (
        form_data.get("code_verifier") or json_data.get("code_verifier")
    )
    req_resource = form_data.get("resource") or json_data.get("resource")

    if grant_type != "authorization_code":
        raise HTTPException(
            status_code=400,
            detail={"error": "unsupported_grant_type"},
        )

    # Strict client verification on token requests
    validate_client(client_id, redirect_uri)

    # Replay protection: find and immediately delete code in a single atomic-like sequence
    db_code = await validate_and_consume_code(
        db=db,
        code=code,
        client_id=client_id,
        redirect_uri=redirect_uri,
        code_verifier=code_verifier,
    )

    # Bind token to target audience resource indicator (RFC 8707)
    target_resource = (
        db_code.resource or req_resource or "http://localhost:8001"
    )

    token_data = {
        "sub": db_code.username,
        "role": db_code.role,
        "client_id": client_id,
        "aud": target_resource,
    }

    access_token = create_access_token(data=token_data)
    response_data = {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": get_settings().ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }

    # Generate standard OIDC ID token if openid scope is requested
    requested_scopes = [
        s.strip() for s in (db_code.scope or "").split() if s.strip()
    ]
    if "openid" in requested_scopes:
        id_token_payload = {
            "iss": f"{request.url.scheme}://{request.url.netloc}",
            "sub": db_code.username,
            "aud": client_id,
            "iat": datetime.now(UTC),
            "role": db_code.role,
        }
        id_token = create_access_token(data=id_token_payload)
        response_data["id_token"] = id_token

    # Generate and bind refresh token for long-term session maintenance (OAuth 2.1 compliance)
    result = await db.execute(select(User).where(User.username == db_code.username))
    user = result.scalars().first()
    if user and isinstance(user, User):
        refresh_token = create_refresh_token(data={"sub": user.username, "role": user.role})
        expires_days = get_settings().REFRESH_TOKEN_EXPIRE_DAYS
        new_rt = RefreshToken(
            token=refresh_token,
            user_id=user.id,
            expires_at=datetime.now(UTC).replace(tzinfo=None) + timedelta(days=expires_days),
        )
        db.add(new_rt)
        await db.commit()

        # Set refresh token in HttpOnly cookie on client response
        secure_flag = request.url.scheme == "https"
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=secure_flag,
            samesite="lax",
            path="/"
        )
        response_data["refresh_token"] = refresh_token

    return response_data


@router.get("/oauth/userinfo")
async def oauth_userinfo(request: Request, db: AsyncSession = Depends(get_db)):
    """Serve the standard OIDC UserInfo endpoint returning user profile claims."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header.replace("Bearer ", "")
    secret = get_settings().JWT_SECRET.get_secret_value()

    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=401,
            detail="Token missing subject claim",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return {
        "sub": user.username,
        "role": user.role,
    }
