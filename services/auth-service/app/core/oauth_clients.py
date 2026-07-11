"""OAuth 2.1 static client registry and validation utilities."""

from fastapi import HTTPException, status

VALID_CLIENTS = {
    "ems-mcp-server": {
        "client_name": "EMS MCP Server",
        "redirect_uris": [
            "http://localhost:8001/callback",
            "http://127.0.0.1:8001/callback",
        ],
        "public": True,
    },
    "keys-personal-assist-ui": {
        "client_name": "Bella Keys Personal Assist UI",
        "redirect_uris": [
            "http://localhost:3000/callback",
            "http://127.0.0.1:3000/callback",
            "bella-app://callback",
        ],
        "public": True,
    },
}


def validate_client(client_id: str, redirect_uri: str) -> dict:
    """Validate client existence and exact redirect URI matching.

    Raises:
        HTTPException: If client is invalid or redirect URI does not match.
    """
    client = VALID_CLIENTS.get(client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_client",
                "error_description": f"Client '{client_id}' is not registered.",
            },
        )

    if redirect_uri not in client["redirect_uris"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_request",
                "error_description": "Redirect URI mismatch.",
            },
        )

    return client
