"""Central OAuth 2.1 scope registry.

This module is the single source of truth for:
- All valid scopes supported by the authorization server.
- Per-client allowed scope sets (what each registered client is permitted to request).

Scope naming convention: <bella-service>:<action>
  - bella-ems:read   -- read-only access to Expense Manager Service resources
  - bella-ems:write  -- write access (create / update / delete) to EMS resources
  - bella-chat:read  -- read-only access to Bella Chat Service resources
  - bella-chat:write -- write access to Chat resources (send messages, manage sessions)

Standard OIDC scopes (openid, profile, email) are used for identity claims only
and are not tied to any specific resource server.

Scopes are NOT stored in the database. They are a static contract validated at
authorization time and embedded into the issued JWT as the "scope" claim.
"""

# All scopes this authorization server recognizes and may grant.
VALID_SCOPES: set[str] = {
    # OIDC identity scopes
    "openid",
    "profile",
    "email",
    # Expense Manager Service scopes
    "bella-ems:read",
    "bella-ems:write",
    # Bella Chat Service scopes
    "bella-chat:read",
    "bella-chat:write",
}

# Maps each registered client_id to the maximum set of scopes it is allowed to request.
# The auth server silently strips any requested scope not in this set before issuing the code.
CLIENT_ALLOWED_SCOPES: dict[str, set[str]] = {
    # The Bella Keys Personal Assist UI (web + desktop) needs full access to both services.
    "keys-personal-assist-ui": {
        "openid",
        "profile",
        "email",
        "bella-ems:read",
        "bella-ems:write",
        "bella-chat:read",
        "bella-chat:write",
    },
    # The EMS MCP Server calls EMS on behalf of the user -- it needs full EMS access for mutations.
    "ems-mcp-server": {
        "bella-ems:read",
        "bella-ems:write",
    },
}


def filter_scopes(client_id: str, requested_scope: str) -> str:
    """Return only the permitted scopes for a given client from the requested scope string.

    Scopes not in VALID_SCOPES or not in the client allowed set are silently dropped
    (per OAuth 2.1 best practice -- no error, just a reduced grant).

    Args:
        client_id: The registered OAuth client identifier.
        requested_scope: A space-separated string of requested scope values.

    Returns:
        A space-separated string of the permitted scopes (may be empty).
    """
    allowed = CLIENT_ALLOWED_SCOPES.get(client_id, set())
    requested = set(requested_scope.split()) if requested_scope else set()
    # Intersection: only grant scopes that are valid AND allowed for this client
    granted = requested & allowed & VALID_SCOPES
    return " ".join(sorted(granted))
