#!/usr/bin/env python3
import argparse
import os
import re


def update_db_url_password(url_val, user_passwords):
    # Match pattern: protocol://username:password@host/dbname
    # Group 1: protocol://username:
    # Group 2: username (captured for lookup)
    # Group 3: password (to replace)
    # Group 4: @host/dbname
    pattern = r"^(postgresql(?:\+asyncpg)?://([^:]+):)([^@]+)(@.*)$"
    match = re.match(pattern, url_val)
    if match:
        prefix, username, _, suffix = match.groups()
        if username in user_passwords:
            new_password = user_passwords[username]
            return f"{prefix}{new_password}{suffix}"
    return url_val


def update_kv_line(key, value, line):
    # Match pattern: key = "value" or key = value or key="value"
    # Preserves quotes and surrounding whitespace
    pattern = r"^(\s*" + re.escape(key) + r'\s*=\s*)(["\'`]?)(.*?)(["\'`]?\s*)$'
    match = re.match(pattern, line)
    if match:
        prefix, open_quote, _, close_quote = match.groups()
        quote = open_quote if open_quote else ""
        return f"{prefix}{quote}{value}{quote}\n"
    return line


def update_env(path, kv_replacements, user_passwords):
    if not os.path.exists(path):
        print(f"Skipping {path} (does not exist)")
        return

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        updated = False

        # 1. Try explicit key-value replacements first
        for key, val in kv_replacements.items():
            if line.strip().startswith(key):
                line = update_kv_line(key, val, line)
                updated = True
                break

        # 2. Try URL-based password substitution for any postgresql:// value
        if not updated and "=" in line:
            parts = line.split("=", 1)
            k, v = parts[0], parts[1].strip()
            clean_v = v.strip("\"'`")
            if clean_v.startswith("postgresql://") or clean_v.startswith(
                "postgresql+asyncpg://"
            ):
                new_v = update_db_url_password(clean_v, user_passwords)
                quote = '"' if v.startswith('"') else "'" if v.startswith("'") else ""
                indent = parts[0][: len(parts[0]) - len(parts[0].lstrip())]
                line = f"{indent}{k.strip()}={quote}{new_v}{quote}\n"

        new_lines.append(line)

    with open(path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print(f"Successfully updated {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Update environment files with database passwords"
    )
    parser.add_argument("--repo-root", required=True, help="Repository root path")
    parser.add_argument("--ems-pass", required=True, help="Password for ems_user")
    parser.add_argument("--arize-pass", required=True, help="Password for arize_user")
    parser.add_argument(
        "--langgraph-pass", required=True, help="Password for langgraph_user"
    )
    parser.add_argument(
        "--auth-pass",
        required=True,
        help="Password for auth_user",
    )
    parser.add_argument(
        "--pg-pass",
        required=False,
        default="postgres",
        help="Password for postgres superuser",
    )

    args = parser.parse_args()
    repo_root = args.repo_root

    # Map username → password for URL-based substitution across all env files
    user_passwords = {
        "ems_user": args.ems_pass,
        "auth_user": args.auth_pass,
        "postgres": args.pg_pass,
        "arize_user": args.arize_pass,
        "langgraph_user": args.langgraph_pass,
    }

    # 1. docker/.env — KV: bare arize + langgraph password fields; URL: auth + ems DATABASE_URLs
    update_env(
        os.path.join(repo_root, "docker", ".env"),
        {
            "ARIZE_PG_DB_PASSWORD": args.arize_pass,
            "LANGGRAPH_PG_DB_PASSWORD": args.langgraph_pass,
        },
        user_passwords,
    )

    # 2. expense-manager-service/.env — URL only: ems_user password in DATABASE_URL
    update_env(
        os.path.join(repo_root, "services", "expense-manager-service", ".env"),
        {},
        user_passwords,
    )

    # 3. bella-chat-service/.env — KV: bare arize + langgraph password fields (DSNs built at runtime)
    update_env(
        os.path.join(repo_root, "services", "bella-chat-service", ".env"),
        {
            "ARIZE_PG_DB_PASSWORD": args.arize_pass,
            "LANGGRAPH_PG_DB_PASSWORD": args.langgraph_pass,
        },
        user_passwords,
    )

    # 4. auth-service/.env — URL only: auth_user password in DATABASE_URL
    update_env(
        os.path.join(repo_root, "services", "auth-service", ".env"),
        {},
        user_passwords,
    )


if __name__ == "__main__":
    main()
