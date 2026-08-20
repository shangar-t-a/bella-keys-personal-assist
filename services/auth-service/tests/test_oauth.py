"""Unit tests for the OAuth 2.1 endpoints in the Auth Service."""

from datetime import datetime, timedelta, UTC
import uuid

from httpx import ASGITransport, AsyncClient
import pytest
from unittest.mock import AsyncMock, MagicMock

import app.api.routers.oauth as auth_mod
from app.core.security import create_access_token
from app.db.database import get_db
from app.db.models import OAuthAuthorizationCode, User
from app.main import app

mock_db = AsyncMock()
mock_db.add = MagicMock()


async def override_get_db():
    yield mock_db


app.dependency_overrides[get_db] = override_get_db


@pytest.mark.asyncio
async def test_oauth_metadata() -> None:
    """Verify that the discovery endpoint returns compliant OAuth 2.1 metadata."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.get("/.well-known/oauth-authorization-server")
        assert response.status_code == 200
        data = response.json()
        assert data["issuer"] == "http://testserver"
        assert data["authorization_endpoint"] == "http://testserver/oauth/authorize"
        assert data["token_endpoint"] == "http://testserver/oauth/token"
        assert "S256" in data["code_challenge_methods_supported"]
        assert data["client_id_metadata_document_supported"] is True


@pytest.mark.asyncio
async def test_oauth_authorize_get() -> None:
    """Verify that the GET authorize endpoint serves the HTML login/consent form."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        params = {
            "client_id": "ems-mcp-server",
            "redirect_uri": "http://localhost:8001/callback",
            "response_type": "code",
            "code_challenge": "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM",
            "code_challenge_method": "S256",
            "state": "state123",
            "resource": "http://localhost:8001",
        }
        response = await client.get("/oauth/authorize", params=params)
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        body = response.text
        assert "ems-mcp-server" in body
        assert "state123" in body


@pytest.mark.asyncio
async def test_oauth_authorize_post_success() -> None:
    """Verify that a successful authorization POST redirects with a valid code."""
    mock_user = User(
        username="shangar", password_hash="hashed_pw", role="user"
    )

    # Properly mock SQLAlchemy's async execute returning scalars and first()
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = mock_user
    mock_result.scalars.return_value = mock_scalars

    mock_db.execute = AsyncMock(return_value=mock_result)

    # Mock password validation
    original_verify = auth_mod.verify_password
    auth_mod.verify_password = lambda p, h: True

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://testserver"
        ) as client:
            form_data = {
                "client_id": "ems-mcp-server",
                "redirect_uri": "http://localhost:8001/callback",
                "response_type": "code",
                "code_challenge": "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM",
                "code_challenge_method": "S256",
                "state": "state123",
                "resource": "http://localhost:8001",
                "username": "shangar",
                "password": "correct_password",
            }
            response = await client.post("/oauth/authorize", data=form_data)
            assert response.status_code == 303
            location = response.headers["location"]
            assert "http://localhost:8001/callback" in location
            assert "code=" in location
            assert "state=state123" in location
    finally:
        auth_mod.verify_password = original_verify


@pytest.mark.asyncio
async def test_oauth_token_exchange() -> None:
    """Verify that exchanging the code and verifier yields a valid token and OIDC ID Token."""
    code = f"auth_code_{uuid.uuid4().hex}"
    mock_code = OAuthAuthorizationCode(
        code=code,
        client_id="ems-mcp-server",
        redirect_uri="http://localhost:8001/callback",
        code_challenge="E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM",
        code_challenge_method="S256",
        username="shangar",
        role="user",
        resource="http://localhost:8001",
        scope="openid profile",
        expires_at=datetime.now(UTC) + timedelta(minutes=5),
    )

    # Mock SQLAlchemy query execution to return our mock code
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = mock_code
    mock_result.scalars.return_value = mock_scalars

    mock_db.execute = AsyncMock(return_value=mock_result)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        form_data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": "ems-mcp-server",
            "redirect_uri": "http://localhost:8001/callback",
            "code_verifier": "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk",
            "resource": "http://localhost:8001",
        }
        response = await client.post("/oauth/token", data=form_data)
        if response.status_code != 200:
            print("Response error detail:", response.text)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "id_token" in data
        assert data["token_type"] == "Bearer"


@pytest.mark.asyncio
async def test_oauth_userinfo() -> None:
    """Verify that userinfo returns the profile details using a valid access token."""
    mock_user = User(
        username="shangar", password_hash="hashed_pw", role="user"
    )

    # Mock SQLAlchemy query execution to return our mock user
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = mock_user
    mock_result.scalars.return_value = mock_scalars

    mock_db.execute = AsyncMock(return_value=mock_result)

    access_token = create_access_token(data={"sub": "shangar", "role": "user"})

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.get("/oauth/userinfo", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["sub"] == "shangar"
        assert data["role"] == "user"


@pytest.mark.asyncio
async def test_rfc8693_token_exchange() -> None:
    """Verify that RFC 8693 token exchange exchanges a subject token for a target-bounded access token."""
    user_token = create_access_token(data={"sub": "shangar", "role": "user", "scope": "bella-ems:read"})

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        form_data = {
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
            "subject_token": user_token,
            "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
            "client_id": "bella-chat-service",
            "resource": "http://localhost:8001/mcp",
        }
        response = await client.post("/oauth/token", data=form_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "Bearer"
        assert data["issued_token_type"] == "urn:ietf:params:oauth:token-type:access_token"

