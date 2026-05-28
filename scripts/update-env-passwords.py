#!/usr/bin/env python3
import os
import sys
import argparse

def update_env(path, replacements, ems_pass):
    if not os.path.exists(path):
        print(f"Skipping {path} (does not exist)")
        return
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    new_lines = []
    for line in lines:
        # Check standard key-value updates
        for k, v in replacements.items():
            if line.strip().startswith(k):
                parts = line.split('=', 1)
                if len(parts) == 2:
                    indent = parts[0][:len(parts[0]) - len(parts[0].lstrip())]
                    val = parts[1].strip()
                    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                        quote = val[0]
                        line = f"{indent}{k}={quote}{v}{quote}\n"
                    else:
                        line = f"{indent}{k}={v}\n"
        # Special check for postgresql connection urls
        if 'postgresql+asyncpg://ems_user:' in line:
            parts = line.split('@')
            if len(parts) > 1:
                prefix = parts[0]
                subparts = prefix.split('ems_user:')
                if len(subparts) > 1:
                    line = subparts[0] + 'ems_user:' + ems_pass + '@' + '@'.join(parts[1:])
        elif '<password>' in line:
            line = line.replace('<password>', ems_pass)
        new_lines.append(line)
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print(f"Successfully updated {path}")

def main():
    parser = argparse.ArgumentParser(description="Update environment files with database passwords")
    parser.add_argument("--repo-root", required=True, help="Repository root path")
    parser.add_argument("--ems-pass", required=True, help="Password for ems_user")
    parser.add_argument("--ems-test-pass", required=True, help="Password for ems_test_user")
    parser.add_argument("--arize-pass", required=True, help="Password for arize_user")
    parser.add_argument("--langgraph-pass", required=True, help="Password for langgraph_user")
    
    args = parser.parse_args()
    
    repo_root = args.repo_root
    
    # 1. Update docker/.env
    update_env(os.path.join(repo_root, 'docker', '.env'), {
        'EMS_PG_DB_PASSWORD': args.ems_pass,
        'ARIZE_PG_DB_PASSWORD': args.arize_pass,
        'LANGGRAPH_PG_DB_PASSWORD': args.langgraph_pass
    }, args.ems_pass)

    # 2. Update expense-manager-service/.env
    update_env(os.path.join(repo_root, 'services', 'expense-manager-service', '.env'), {
        'PG_DB_PASSWORD': args.ems_pass
    }, args.ems_pass)

    # 3. Update bella-chat-service/.env
    update_env(os.path.join(repo_root, 'services', 'bella-chat-service', '.env'), {
        'ARIZE_PG_DB_PASSWORD': args.arize_pass,
        'LANGGRAPH_POSTGRES_PASSWORD': args.langgraph_pass
    }, args.ems_pass)

if __name__ == "__main__":
    main()
