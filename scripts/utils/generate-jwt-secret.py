#!/usr/bin/env python3
"""Generate a secure JWT secret (hex string, same format as current JWT_SECRET)."""

import secrets

# 32 bytes = 64 hex chars (256-bit) — matches current JWT_SECRET format
print(secrets.token_hex(32))
