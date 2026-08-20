"""Central OAuth 2.1, OIDC, and security constants for Auth Service."""

GRANT_TYPE_AUTHORIZATION_CODE = "authorization_code"
GRANT_TYPE_TOKEN_EXCHANGE = "urn:ietf:params:oauth:grant-type:token-exchange"
ISSUED_TOKEN_TYPE_ACCESS_TOKEN = "urn:ietf:params:oauth:token-type:access_token"

TOKEN_TYPE_BEARER = "Bearer"
TOKEN_TYPE_BEARER_LOWER = "bearer"

CODE_CHALLENGE_METHOD_S256 = "S256"
ALGORITHM_HS256 = "HS256"

COOKIE_REFRESH_TOKEN = "refresh_token"
COOKIE_PATH_ROOT = "/"
COOKIE_SAMESITE_LAX = "lax"

SECONDS_PER_MINUTE = 60
