"""Add liability categories and subcategories seed.

Override ID: 4e9512ef
Down Revision: 3d940e32
Create Date: 2026-06-21 15:53:00.000000
"""

from sqlalchemy import text

CATEGORIES = [
    ("c1c2c3d4e5f64123a789bcde10111213", "Secured Loans", "SECURED_LOAN", "Loans backed by collateral like home, vehicle"),
    ("d1d2d3d4e5f64123a789bcde10111214", "Unsecured Loans", "UNSECURED_LOAN", "Loans with no collateral like personal, education loans"),
    ("e1e2e3d4e5f64123a789bcde10111215", "Revolving Credit", "REVOLVING_CREDIT", "Lines of credit like credit cards"),
    ("f1f2f3d4e5f64123a789bcde10111216", "Other Liabilities", "OTHER", "Family loans, hand loans, or general liabilities"),
]

SUBCATEGORIES = [
    ("c1c2c3d4e5f64123a789bcde10111213", "a1b2c3d4e5f647898b9cdaabcc123456", "Home Loan", "HOME_LOAN", "VALUE_BASED", True, True, "Loan taken to purchase a house, land, or apartment. Requires principal and outstanding balance updates."),
    ("c1c2c3d4e5f64123a789bcde10111213", "a1b2c3d4e5f647898b9cdaabcc123457", "Vehicle Loan", "VEHICLE_LOAN", "VALUE_BASED", True, True, "Car, bike, or commercial vehicle loan. Tracks interest and outstanding balance."),
    ("d1d2d3d4e5f64123a789bcde10111214", "a1b2c3d4e5f647898b9cdaabcc123458", "Personal Loan", "PERSONAL_LOAN", "VALUE_BASED", True, True, "Unsecured personal loan from banks or financial institutions."),
    ("d1d2d3d4e5f64123a789bcde10111214", "a1b2c3d4e5f647898b9cdaabcc123459", "Education Loan", "EDUCATION_LOAN", "VALUE_BASED", True, True, "Student loan taken for education purposes."),
    ("e1e2e3d4e5f64123a789bcde10111215", "a1b2c3d4e5f647898b9cdaabcc123460", "Credit Card Outstanding", "CREDIT_CARD", "VALUE_BASED", True, False, "Outstanding statement balance on credit cards."),
    ("f1f2f3d4e5f64123a789bcde10111216", "a1b2c3d4e5f647898b9cdaabcc123461", "Other Loan/Liability", "OTHER_LIABILITY", "VALUE_BASED", False, False, "Loans from family, hand loans, or general non-interest liabilities."),
]


async def upgrade(session):
    # 1. Insert or update categories
    for cat_id, name, code, desc in CATEGORIES:
        res = await session.execute(text("SELECT id FROM liability_category WHERE code = :code"), {"code": code})
        existing = res.fetchone()

        if existing:
            print(f"Updating liability category: {code}")
            await session.execute(
                text("UPDATE liability_category SET name = :name, description = :desc, updated_at = NOW() WHERE code = :code"),
                {"name": name, "desc": desc, "code": code},
            )
        else:
            print(f"Creating liability category: {code}")
            await session.execute(
                text(
                    "INSERT INTO liability_category (id, name, code, description, created_at, updated_at) "
                    "VALUES (:id, :name, :code, :desc, NOW(), NOW())"
                ),
                {"id": cat_id, "name": name, "code": code, "desc": desc},
            )

    # 2. Insert or update subcategories
    for cat_id, sub_id, name, code, val_type, has_interest, has_maturity, desc in SUBCATEGORIES:
        res = await session.execute(text("SELECT id FROM liability_subcategory WHERE code = :code"), {"code": code})
        existing = res.fetchone()

        if existing:
            print(f"Updating liability subcategory: {code}")
            await session.execute(
                text(
                    "UPDATE liability_subcategory "
                    "SET category_id = :cat_id, name = :name, description = :desc, "
                    "    valuation_type = :val_type, has_interest = :has_interest, has_maturity = :has_maturity, "
                    "    updated_at = NOW() "
                    "WHERE code = :code"
                ),
                {
                    "cat_id": cat_id,
                    "name": name,
                    "desc": desc,
                    "val_type": val_type,
                    "has_interest": has_interest,
                    "has_maturity": has_maturity,
                    "code": code,
                },
            )
        else:
            print(f"Creating liability subcategory: {code}")
            await session.execute(
                text(
                    "INSERT INTO liability_subcategory (id, category_id, name, code, description, valuation_type, has_interest, has_maturity, created_at, updated_at) "
                    "VALUES (:id, :cat_id, :name, :code, :desc, :val_type, :has_interest, :has_maturity, NOW(), NOW())"
                ),
                {
                    "id": sub_id,
                    "cat_id": cat_id,
                    "name": name,
                    "code": code,
                    "desc": desc,
                    "val_type": val_type,
                    "has_interest": has_interest,
                    "has_maturity": has_maturity,
                },
            )
