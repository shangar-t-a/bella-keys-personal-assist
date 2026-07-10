"""Pydantic and Form schemas for OAuth 2.1 authorization request parsing."""

from fastapi import Form
from pydantic import BaseModel


class OAuthAuthorizeParams(BaseModel):
    """Pydantic model to group OAuth authorization GET parameters."""

    client_id: str
    redirect_uri: str
    response_type: str
    code_challenge: str
    code_challenge_method: str
    state: str = ""
    resource: str = ""
    scope: str = ""


class OAuthAuthorizeForm:
    """Dependency helper to group OAuth authorization POST form parameters."""

    def __init__(  # noqa: PLR0913
        self,
        client_id: str = Form(...),
        redirect_uri: str = Form(...),
        response_type: str = Form(...),
        code_challenge: str = Form(...),
        code_challenge_method: str = Form(...),
        state: str = Form(""),
        resource: str = Form(""),
        scope: str = Form(""),
        username: str = Form(...),
        password: str = Form(...),
    ):
        """Initialize the authorization form parameters."""
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.response_type = response_type
        self.code_challenge = code_challenge
        self.code_challenge_method = code_challenge_method
        self.state = state
        self.resource = resource
        self.scope = scope
        self.username = username
        self.password = password
