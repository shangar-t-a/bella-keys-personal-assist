"""API Router for OAuth 2.1 endpoints."""

import contextlib
import os
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

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
from app.core.constants import (
    ALGORITHM_HS256,
    CODE_CHALLENGE_METHOD_S256,
    GRANT_TYPE_AUTHORIZATION_CODE,
    GRANT_TYPE_TOKEN_EXCHANGE,
    ISSUED_TOKEN_TYPE_ACCESS_TOKEN,
    SECONDS_PER_MINUTE,
    TOKEN_TYPE_BEARER,
)
from app.core.cookies import set_refresh_token_cookie
from app.core.oauth_clients import validate_client
from app.core.scopes import VALID_SCOPES, filter_scopes
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
)
from app.db.database import get_db
from app.db.models import RefreshToken, User
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
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


def _extract_client_name(client_id: str) -> str:
    """Extract display client name from client_id URI or string identifier."""
    name = client_id.rsplit("/", 1)[-1] if "/" in client_id else client_id
    if name.endswith(".json"):
        name = name[:-5]
    return name


def _build_authorize_context(
    request: Request,
    params: OAuthAuthorizeParams | OAuthAuthorizeForm,
    error_html: str = "",
) -> dict[str, Any]:
    """Construct standardized template context dictionary for authorize form."""
    return {
        "client_name": _extract_client_name(params.client_id),
        "client_id": params.client_id,
        "redirect_uri": params.redirect_uri,
        "response_type": params.response_type,
        "code_challenge": params.code_challenge,
        "code_challenge_method": params.code_challenge_method,
        "state": params.state or "",
        "resource": params.resource or "",
        "scope": params.scope or "",
        "error_html": error_html,
    }


async def _parse_token_request_body(request: Request) -> tuple[dict[str, Any], dict[str, Any]]:
    """Attempt to parse both form-urlencoded and JSON request payloads."""
    form_data: dict[str, Any] = {}
    with contextlib.suppress(Exception):
        form_data = dict(await request.form())

    json_data: dict[str, Any] = {}
    with contextlib.suppress(Exception):
        json_data = await request.json()

    return form_data, json_data


@router.get("/.well-known/oauth-authorization-server")
@router.get("/.well-known/openid-configuration")
async def oauth_metadata(request: Request) -> dict[str, Any]:
    """Serve metadata configuration for OAuth 2.1 / OIDC discovery."""
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    return {
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/oauth/authorize",
        "token_endpoint": f"{base_url}/oauth/token",
        "userinfo_endpoint": f"{base_url}/oauth/userinfo",
        "response_types_supported": ["code"],
        "grant_types_supported": [GRANT_TYPE_AUTHORIZATION_CODE, GRANT_TYPE_TOKEN_EXCHANGE],
        "code_challenge_methods_supported": [CODE_CHALLENGE_METHOD_S256],
        "scopes_supported": sorted(VALID_SCOPES),
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": [ALGORITHM_HS256],
        "client_id_metadata_document_supported": True,
    }


@router.get("/oauth/authorize", response_class=HTMLResponse)
async def oauth_authorize_get(
    request: Request,
    params: OAuthAuthorizeParams = Depends(),
) -> HTMLResponse:
    """Render the OAuth 2.1 login and consent form."""
    validate_client(params.client_id, params.redirect_uri)
    context = _build_authorize_context(request=request, params=params)
    return templates.TemplateResponse(request=request, name="authorize.html", context=context)


@router.post("/oauth/authorize", response_class=HTMLResponse)
async def oauth_authorize_post(
    request: Request,
    form: OAuthAuthorizeForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Authenticate credentials and redirect back with authorization code."""
    validate_client(form.client_id, form.redirect_uri)

    result = await db.execute(select(User).where(User.username == form.username))
    user = result.scalars().first()

    if not user or not verify_password(form.password, user.password_hash):
        context = _build_authorize_context(request=request, params=form, error_html="Incorrect username or password")
        return templates.TemplateResponse(request=request, name="authorize.html", context=context, status_code=401)

    await prune_expired_codes(db)

    validated_scope = filter_scopes(form.client_id, form.scope or "")
    code = await create_authorization_code(
        db=db,
        client_id=form.client_id,
        redirect_uri=form.redirect_uri,
        code_challenge=form.code_challenge,
        code_challenge_method=form.code_challenge_method,
        username=form.username,
        role=user.role,
        resource=form.resource,
        scope=validated_scope,
    )

    rt_payload = {
        "sub": user.username,
        "role": user.role,
        "client_id": form.client_id,
        "scope": form.scope or "",
        "aud": form.resource or get_settings().DEFAULT_RESOURCE_AUDIENCE,
    }
    refresh_token = create_refresh_token(data=rt_payload)
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

    secure_flag = request.url.scheme == "https"

    if form.redirect_uri.startswith("http://") or form.redirect_uri.startswith("https://"):
        redirect_response = RedirectResponse(url=redirect_url, status_code=303)
        set_refresh_token_cookie(redirect_response, refresh_token, secure_flag)
        return redirect_response

    success_response = templates.TemplateResponse(
        request=request,
        name="success.html",
        context={"redirect_url": redirect_url},
    )
    set_refresh_token_cookie(success_response, refresh_token, secure_flag)
    return success_response


def _handle_token_exchange(
    form_data: dict[str, Any],
    json_data: dict[str, Any],
    client_id: str | None,
    req_resource: str | None,
    base_url: str,
) -> dict[str, Any]:
    """Process RFC 8693 OAuth 2.0 Token Exchange (On-Behalf-Of) request."""
    subject_token = form_data.get("subject_token") or json_data.get("subject_token")
    if not subject_token:
        raise HTTPException(
            status_code=400,
            detail={"error": "invalid_request", "error_description": "Missing subject_token for token-exchange"},
        )

    secret = get_settings().JWT_SECRET.get_secret_value()
    try:
        payload = jwt.decode(
            subject_token, secret, algorithms=[ALGORITHM_HS256], options={"verify_aud": False}
        )
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail={"error": "invalid_grant", "error_description": f"Invalid subject_token: {e}"},
        ) from e

    target_resource = req_resource or get_settings().DEFAULT_RESOURCE_AUDIENCE
    actor_sub = client_id or payload.get("client_id", "client_service")

    token_data = {
        "iss": base_url,
        "sub": payload.get("sub"),
        "aud": target_resource,
        "client_id": actor_sub,
        "iat": datetime.now(UTC),
        "nbf": datetime.now(UTC),
        "jti": uuid.uuid4().hex,
        "scope": payload.get("scope", ""),
        "role": payload.get("role", "user"),
        "act": {"sub": actor_sub},
    }

    access_token = create_access_token(data=token_data)
    return {
        "access_token": access_token,
        "token_type": TOKEN_TYPE_BEARER,
        "expires_in": get_settings().ACCESS_TOKEN_EXPIRE_MINUTES * SECONDS_PER_MINUTE,
        "issued_token_type": ISSUED_TOKEN_TYPE_ACCESS_TOKEN,
    }


@router.post("/oauth/token")
async def oauth_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Exchange authorization code or subject token for JWT access token."""
    await prune_expired_codes(db)

    form_data, json_data = await _parse_token_request_body(request)

    grant_type = form_data.get("grant_type") or json_data.get("grant_type")
    client_id = form_data.get("client_id") or json_data.get("client_id")
    req_resource = (
        form_data.get("resource") or json_data.get("resource") or form_data.get("audience") or json_data.get("audience")
    )
    base_url = f"{request.url.scheme}://{request.url.netloc}"

    if grant_type == GRANT_TYPE_TOKEN_EXCHANGE:
        return _handle_token_exchange(form_data, json_data, client_id, req_resource, base_url)

    if grant_type != GRANT_TYPE_AUTHORIZATION_CODE:
        raise HTTPException(
            status_code=400,
            detail={"error": "unsupported_grant_type"},
        )

    code = form_data.get("code") or json_data.get("code")
    redirect_uri = form_data.get("redirect_uri") or json_data.get("redirect_uri")
    code_verifier = form_data.get("code_verifier") or json_data.get("code_verifier")

    validate_client(client_id, redirect_uri)

    db_code = await validate_and_consume_code(
        db=db,
        code=code,
        client_id=client_id,
        redirect_uri=redirect_uri,
        code_verifier=code_verifier,
    )

    target_resource = db_code.resource or req_resource or get_settings().DEFAULT_RESOURCE_AUDIENCE

    token_data = {
        "iss": base_url,
        "sub": db_code.username,
        "aud": target_resource,
        "client_id": client_id,
        "iat": datetime.now(UTC),
        "nbf": datetime.now(UTC),
        "jti": uuid.uuid4().hex,
        "scope": db_code.scope or "",
        "role": db_code.role,
    }

    access_token = create_access_token(data=token_data)
    response_data = {
        "access_token": access_token,
        "token_type": TOKEN_TYPE_BEARER,
        "expires_in": get_settings().ACCESS_TOKEN_EXPIRE_MINUTES * SECONDS_PER_MINUTE,
    }

    requested_scopes = [s.strip() for s in (db_code.scope or "").split() if s.strip()]
    if "openid" in requested_scopes:
        id_token_payload = {
            "iss": base_url,
            "sub": db_code.username,
            "aud": client_id,
            "iat": datetime.now(UTC),
            "role": db_code.role,
        }
        response_data["id_token"] = create_access_token(data=id_token_payload)

    result = await db.execute(select(User).where(User.username == db_code.username))
    user = result.scalars().first()
    if user and isinstance(user, User):
        rt_payload = {
            "sub": user.username,
            "role": user.role,
            "client_id": client_id,
            "scope": db_code.scope or "",
            "aud": target_resource,
        }
        refresh_token = create_refresh_token(data=rt_payload)
        expires_days = get_settings().REFRESH_TOKEN_EXPIRE_DAYS
        new_rt = RefreshToken(
            token=refresh_token,
            user_id=user.id,
            expires_at=datetime.now(UTC).replace(tzinfo=None) + timedelta(days=expires_days),
        )
        db.add(new_rt)
        await db.commit()

        secure_flag = request.url.scheme == "https"
        set_refresh_token_cookie(response, refresh_token, secure_flag)
        response_data["refresh_token"] = refresh_token

    return response_data


@router.get("/oauth/userinfo")
async def oauth_userinfo(request: Request, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """Serve standard OIDC UserInfo endpoint returning user profile claims."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith(f"{TOKEN_TYPE_BEARER} "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": TOKEN_TYPE_BEARER},
        )

    token = auth_header.replace(f"{TOKEN_TYPE_BEARER} ", "")
    secret = get_settings().JWT_SECRET.get_secret_value()

    try:
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM_HS256])
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {e}",
            headers={"WWW-Authenticate": TOKEN_TYPE_BEARER},
        ) from e

    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=401,
            detail="Token missing subject claim",
            headers={"WWW-Authenticate": TOKEN_TYPE_BEARER},
        )

    result = await db.execute(select(User).where(User.username == username))
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
