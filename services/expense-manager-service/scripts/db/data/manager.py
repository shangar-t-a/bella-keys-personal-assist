import importlib.util
import os
import sys

from sqlalchemy import text

# Ensure we can import app and data module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from scripts.db.data.utils import get_session_maker


async def run_data_migrations():
    session_maker = get_session_maker()
    async with session_maker() as session:
        # Create version tracking table if it doesn't exist
        await session.execute(
            text(
                "CREATE TABLE IF NOT EXISTS data_migration_version ("
                "    version_num VARCHAR(32) PRIMARY KEY,"
                "    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
                ")"
            )
        )
        await session.commit()

        # Get already applied versions
        res = await session.execute(text("SELECT version_num FROM data_migration_version"))
        applied_versions = {row[0] for row in res.fetchall()}

        # Find all version files
        versions_dir = os.path.join(os.path.dirname(__file__), "versions")
        if not os.path.exists(versions_dir):
            print(f"Versions directory not found at {versions_dir}. Creating it.")
            os.makedirs(versions_dir)

        raw_migrations = []
        for file in os.listdir(versions_dir):
            if file.endswith(".py") and "_" in file:
                filepath = os.path.join(versions_dir, file)
                override_id = None
                down_revision = None
                with open(filepath, encoding="utf-8") as f:
                    for line in f:
                        if "Override ID:" in line:
                            override_id = line.split("Override ID:")[1].strip()
                        elif "Down Revision:" in line:
                            down_revision = line.split("Down Revision:")[1].strip()
                            if down_revision.lower() == "none":
                                down_revision = None
                if override_id:
                    raw_migrations.append(
                        {"override_id": override_id, "down_revision": down_revision, "filename": file}
                    )

        # Sort migrations topologically based on down_revision chain
        by_down = {}
        start_nodes = []
        for m in raw_migrations:
            down = m["down_revision"]
            if not down:
                start_nodes.append(m)
            else:
                by_down.setdefault(down, []).append(m)

        ordered_migrations = []

        def visit(node):
            ordered_migrations.append(node)
            for child in by_down.get(node["override_id"], []):
                visit(child)

        for start in start_nodes:
            visit(start)

        # Run unapplied migrations
        for migration in ordered_migrations:
            override_id = migration["override_id"]
            filename = migration["filename"]
            if override_id not in applied_versions:
                print(f"Running data migration: {filename} (Override ID: {override_id})")

                # Import module dynamically
                module_path = os.path.join(versions_dir, filename)
                spec = importlib.util.spec_from_file_location(override_id, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Run upgrade
                await module.upgrade(session)

                # Record migration as applied
                await session.execute(
                    text("INSERT INTO data_migration_version (version_num) VALUES (:version)"), {"version": override_id}
                )
                await session.commit()
                print(f"Successfully applied: {filename}")
            else:
                print(f"Data migration already applied: {filename}")

        # Write/update latest_version.txt on the host disk if we ran migrations
        if ordered_migrations:
            latest_hash = ordered_migrations[-1]["override_id"]
            latest_version_file = os.path.join(os.path.dirname(__file__), "latest_version.txt")
            with open(latest_version_file, "w") as f:
                f.write(latest_hash + "\n")
            print(f"Latest version file updated to: {latest_hash}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_data_migrations())
