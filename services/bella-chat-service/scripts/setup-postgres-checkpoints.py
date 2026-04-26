"""LangGraph Postgres checkpointer setup script.

Sets up everything needed for the LangGraph checkpointer from scratch:
  1. Verifies / creates the app user
  2. Grants all required privileges to the app user
  3. Verifies / creates the checkpoint database
  4. Initializes LangGraph checkpoint tables

Works for fresh installs, partial setups, and existing setups.

Usage:
    # Uses only .env (app user must already exist and have sufficient access)
    python setup-postgres-checkpoints.py

    # Provide superuser credentials to handle user/db creation automatically
    python setup-postgres-checkpoints.py --su-user postgres --su-password <pass>
"""

import argparse
import asyncio
import getpass
import os
import sys

import psycopg
from dotenv import load_dotenv
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

load_dotenv()

# ---------------------------------------------------------------------------
# Parse CLI args
# ---------------------------------------------------------------------------
parser = argparse.ArgumentParser(description="Set up LangGraph Postgres checkpointer")
parser.add_argument("--su-user", default=None, help="Postgres superuser name (e.g. postgres)")
parser.add_argument("--su-password", default=None, help="Postgres superuser password")
args = parser.parse_args()

# ---------------------------------------------------------------------------
# Load app credentials from .env
# ---------------------------------------------------------------------------
user = os.getenv("LANGGRAPH_PG_DB_USER")
password = os.getenv("LANGGRAPH_PG_DB_PASSWORD")
host = os.getenv("LANGGRAPH_PG_DB_HOST")
db_name = os.getenv("LANGGRAPH_PG_DB_NAME")

required_vars = {
    "LANGGRAPH_PG_DB_USER": user,
    "LANGGRAPH_PG_DB_PASSWORD": password,
    "LANGGRAPH_PG_DB_HOST": host,
    "LANGGRAPH_PG_DB_NAME": db_name,
}
missing = [name for name, val in required_vars.items() if not val]
if missing:
    print(f"❌ Missing required .env variables: {', '.join(missing)}")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Resolve superuser credentials
# ---------------------------------------------------------------------------
su_user: str = args.su_user or ""
su_password: str = args.su_password or ""

if not su_user:
    su_user = input("Superuser name [postgres]: ").strip() or "postgres"
if not su_password:
    su_password = getpass.getpass(f"Password for '{su_user}': ")

APP_DSN = f"postgresql://{user}:{password}@{host}:5432/{db_name}"
SU_DSN = f"postgresql://{su_user}:{su_password}@{host}:5432/postgres"


# ---------------------------------------------------------------------------
# Step helpers
# ---------------------------------------------------------------------------


async def step_ensure_user(conn: psycopg.AsyncConnection) -> bool:
    """Create the app user if it does not exist, then set its password."""
    print(f"\n[1/3] Checking app user '{user}'...")
    result = await conn.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (user,))
    row = await result.fetchone()
    if row:
        print(f"  ✅ User '{user}' already exists.")
    else:
        print(f"  ℹ️  User '{user}' not found. Creating...")
        await conn.execute(f'CREATE ROLE "{user}" LOGIN PASSWORD %s', (password,))
        print(f"  ✅ User '{user}' created.")
    return True


async def step_grant_privileges(conn: psycopg.AsyncConnection) -> bool:
    """Grant all required privileges to the app user on the target database."""
    print(f"\n[2/3] Granting privileges on database '{db_name}' to '{user}'...")

    # Check if the DB exists first; we can only GRANT on an existing DB
    result = await conn.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
    db_exists = await result.fetchone()

    if not db_exists:
        print(f"  ℹ️  Database '{db_name}' not found. Creating...")
        await conn.execute(f'CREATE DATABASE "{db_name}"')
        print(f"  ✅ Database '{db_name}' created.")

    await conn.execute(f'GRANT ALL PRIVILEGES ON DATABASE "{db_name}" TO "{user}"')
    print("  ✅ GRANT ALL PRIVILEGES ON DATABASE done.")

    # Also grant schema-level access inside the target DB
    async with await psycopg.AsyncConnection.connect(
        f"postgresql://{su_user}:{su_password}@{host}:5432/{db_name}", autocommit=True
    ) as db_conn:
        await db_conn.execute(f'GRANT ALL ON SCHEMA public TO "{user}"')
        await db_conn.execute(f'ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO "{user}"')
        await db_conn.execute(f'ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO "{user}"')
    print("  ✅ Schema-level privileges granted.")
    return True


async def step_init_checkpointer() -> bool:
    """Initialize LangGraph checkpoint tables."""
    print(f"\n[3/3] Initializing LangGraph checkpoint tables in '{db_name}'...")
    async with AsyncPostgresSaver.from_conn_string(APP_DSN) as checkpointer:
        await checkpointer.setup()
    print("  ✅ Checkpoint tables initialized.")
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def main() -> int:
    """Main setup flow."""
    print("=== LangGraph Postgres Setup ===")
    print(f"  Host     : {host}:5432")
    print(f"  Database : {db_name}")
    print(f"  App user : {user}")
    print(f"  Superuser: {su_user}")

    try:
        async with await psycopg.AsyncConnection.connect(SU_DSN, autocommit=True) as conn:
            if not await step_ensure_user(conn):
                return 1
            if not await step_grant_privileges(conn):
                return 1
    except Exception as e:
        print(f"\n❌ Could not connect as superuser '{su_user}': {e}")
        print("  Check --su-user / --su-password and ensure Postgres is running.")
        return 1

    try:
        if not await step_init_checkpointer():
            return 1
    except Exception as e:
        print(f"\n❌ Failed to initialize checkpointer: {e}")
        return 1

    print("\n✅ Setup complete! LangGraph checkpointer is ready.")
    return 0


if __name__ == "__main__":
    import selectors

    sys.exit(asyncio.run(main(), loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector())))
