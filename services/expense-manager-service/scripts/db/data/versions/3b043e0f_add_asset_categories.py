"""Add asset categories seed.

Revision ID: cf75512f371a
Override ID: 3b043e0f
Down Revision: None
Create Date: 2026-06-06 19:20:00.000000
"""

from sqlalchemy import text

CATEGORIES = [
    ("5d287bc128794c4fae855f75e7a9e6b1", "Equity", "EQUITY", "Stocks, Mutual Funds, ETFs"),
    ("2f4a47da2f174780a424e7561a09d3b4", "Debt", "DEBT", "Fixed Deposits, PPF, Bonds, EPF"),
    ("e439bb7f10b741008d5b88c426f6e522", "Real Estate", "REAL_ESTATE", "Land, Residential/Commercial Properties"),
    ("a434c382103b417e914e9f7823f6e111", "Commodities", "COMMODITIES", "Physical/Digital Gold, Silver"),
    ("c831c382123b417e914e9f7823f6e222", "Cash / Bank", "CASH_BANK", "Savings accounts, Cash"),
]


async def upgrade(session):
    for cat_id, name, code, desc in CATEGORIES:
        res = await session.execute(text("SELECT id, name FROM asset_category WHERE code = :code"), {"code": code})
        existing = res.fetchone()

        if existing:
            old_id = existing[0]
            old_name = existing[1]
            if old_id != cat_id:
                print(f"Updating category ID for {code}: {old_id} -> {cat_id}")
                # 1. Temporarily rename old code and name to avoid unique constraint violations
                await session.execute(
                    text("UPDATE asset_category SET code = :old_code, name = :old_name WHERE id = :old_id"),
                    {"old_code": code + "_old", "old_name": old_name + " (Old)", "old_id": old_id},
                )
                # 2. Insert new category with correct UUID ID
                await session.execute(
                    text(
                        "INSERT INTO asset_category (id, name, code, description, created_at, updated_at) "
                        "VALUES (:id, :name, :code, :desc, NOW(), NOW())"
                    ),
                    {"id": cat_id, "name": name, "code": code, "desc": desc},
                )
                # 3. Update references in asset and asset_subcategory
                await session.execute(
                    text("UPDATE asset SET category_id = :new_id WHERE category_id = :old_id"),
                    {"new_id": cat_id, "old_id": old_id},
                )
                await session.execute(
                    text("UPDATE asset_subcategory SET category_id = :new_id WHERE category_id = :old_id"),
                    {"new_id": cat_id, "old_id": old_id},
                )
                # 4. Delete old category record
                await session.execute(text("DELETE FROM asset_category WHERE id = :old_id"), {"old_id": old_id})
            else:
                print(f"Updating category: {code}")
                await session.execute(
                    text("UPDATE asset_category SET name = :name, description = :desc WHERE code = :code"),
                    {"name": name, "desc": desc, "code": code},
                )
        else:
            print(f"Creating category: {code}")
            await session.execute(
                text(
                    "INSERT INTO asset_category (id, name, code, description, created_at, updated_at) "
                    "VALUES (:id, :name, :code, :desc, NOW(), NOW())"
                ),
                {"id": cat_id, "name": name, "code": code, "desc": desc},
            )
