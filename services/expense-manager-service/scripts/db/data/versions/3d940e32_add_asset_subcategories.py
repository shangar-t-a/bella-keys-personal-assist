"""Add asset subcategories and descriptions seed.

Revision ID: 9a00a9672c95
Override ID: 3d940e32
Down Revision: 3b043e0f
Create Date: 2026-06-06 19:10:00.000000
"""

from sqlalchemy import select, text

from app.infrastructures.postgres_db.models.asset_subcategory import AssetSubcategoryModel

SUBCATEGORIES = [
    ("5d287bc128794c4fae855f75e7a9e6b1", "Stock", "STOCK", "UNIT_BASED", False, False),
    ("5d287bc128794c4fae855f75e7a9e6b1", "Mutual Fund", "MUTUAL_FUND", "UNIT_BASED", False, False),
    ("5d287bc128794c4fae855f75e7a9e6b1", "ETF", "ETF", "UNIT_BASED", False, False),
    ("5d287bc128794c4fae855f75e7a9e6b1", "NPS", "NPS_EQUITY", "UNIT_BASED", False, True),
    ("5d287bc128794c4fae855f75e7a9e6b1", "Other Equity", "OTHER_EQUITY", "UNIT_BASED", False, False),
    ("2f4a47da2f174780a424e7561a09d3b4", "PPF", "PPF", "VALUE_BASED", True, True),
    ("2f4a47da2f174780a424e7561a09d3b4", "EPF / VPF", "EPF_VPF", "VALUE_BASED", True, False),
    ("2f4a47da2f174780a424e7561a09d3b4", "NPS", "NPS_DEBT", "VALUE_BASED", True, True),
    ("2f4a47da2f174780a424e7561a09d3b4", "SSY", "SSY", "VALUE_BASED", True, True),
    ("2f4a47da2f174780a424e7561a09d3b4", "Govt. Savings Scheme", "GOVT_SAVINGS", "VALUE_BASED", True, True),
    ("2f4a47da2f174780a424e7561a09d3b4", "Fixed Deposit", "FIXED_DEPOSIT", "VALUE_BASED", True, True),
    ("2f4a47da2f174780a424e7561a09d3b4", "Recurring Deposit", "RECURRING_DEPOSIT", "VALUE_BASED", True, True),
    ("2f4a47da2f174780a424e7561a09d3b4", "Bonds", "BONDS", "UNIT_BASED", True, True),
    ("2f4a47da2f174780a424e7561a09d3b4", "Other Debt", "OTHER_DEBT", "VALUE_BASED", False, False),
    ("e439bb7f10b741008d5b88c426f6e522", "Residential Property", "RESIDENTIAL", "VALUE_BASED", False, False),
    ("e439bb7f10b741008d5b88c426f6e522", "Commercial Property", "COMMERCIAL", "VALUE_BASED", False, False),
    ("e439bb7f10b741008d5b88c426f6e522", "Plot", "PLOT", "VALUE_BASED", False, False),
    ("e439bb7f10b741008d5b88c426f6e522", "REIT", "REIT", "UNIT_BASED", False, False),
    ("e439bb7f10b741008d5b88c426f6e522", "Other Property", "OTHER_PROPERTY", "VALUE_BASED", False, False),
    ("a434c382103b417e914e9f7823f6e111", "Physical Gold / Silver", "PHYSICAL_GOLD_SILVER", "UNIT_BASED", False, False),
    ("a434c382103b417e914e9f7823f6e111", "Digital (ETF / SGB / MF)", "DIGITAL_COMMODITIES", "UNIT_BASED", False, False),
    ("a434c382103b417e914e9f7823f6e111", "Sovereign Gold Bond", "SGB", "UNIT_BASED", True, True),
    ("c831c382123b417e914e9f7823f6e222", "Savings Account", "SAVINGS_ACCOUNT", "VALUE_BASED", True, False),
    ("c831c382123b417e914e9f7823f6e222", "Current Account", "CURRENT_ACCOUNT", "VALUE_BASED", False, False),
    ("c831c382123b417e914e9f7823f6e222", "Cash in Hand", "CASH_IN_HAND", "VALUE_BASED", False, False),
    ("c831c382123b417e914e9f7823f6e222", "Other Cash", "OTHER_CASH", "VALUE_BASED", False, False),
]
SUBCATEGORY_UUIDS = {
    "STOCK": "b76e3bb81d914dcc8efee7ebaab729e3",
    "MUTUAL_FUND": "a17f5a448d4f49ebaf8e3fa8c67bb017",
    "ETF": "d9856bc7790645698596b198a3adabdb",
    "NPS_EQUITY": "508a0815b9dd4531887215cbc7b137ba",
    "OTHER_EQUITY": "29d07153246145e1b0fc623d32579587",
    "PPF": "504bdb52c67c43558f901550cc05fdac",
    "EPF_VPF": "d3e88c2771854efb8cbd482398c07f09",
    "NPS_DEBT": "0516d3ebca164012b7132179394a60ce",
    "SSY": "d3d6cb93005848a6bb64ee9e875d98bc",
    "GOVT_SAVINGS": "a7ad1440461a494d88821af459c056ae",
    "FIXED_DEPOSIT": "efd80643f5804f50b8a0105bcd357e66",
    "RECURRING_DEPOSIT": "e1462f9b4e1a471f8a3c056bba51043d",
    "BONDS": "82c43e3cb0e549b48c75d093cd1ddcc2",
    "OTHER_DEBT": "4ff381d513014ec2bfebb316e7992243",
    "RESIDENTIAL": "ed6f0835c470429d89f3da23886aa80e",
    "COMMERCIAL": "52ccd9409aac47038edb6e77f07810a6",
    "PLOT": "a25e621de9d34236b629e56918e93755",
    "REIT": "32c5c9e280b94c0fb2e0c99af82432b9",
    "OTHER_PROPERTY": "b07f024c8c1d4a2fad46a9e01a1e371b",
    "PHYSICAL_GOLD_SILVER": "cd4b7b9032ab4cd5865e00a1ad253b8c",
    "DIGITAL_COMMODITIES": "a900c765d2dd42baaff22a1f37bce5f6",
    "SGB": "9083ba87419d461a8729beaaa82e8938",
    "SAVINGS_ACCOUNT": "332745c8f9a84d95ace11a2ff2e0c637",
    "CURRENT_ACCOUNT": "e8b18c3678bc47a58aff6f23e5f1469b",
    "CASH_IN_HAND": "117f8903068d467482a1037c87d0e2c2",
    "OTHER_CASH": "f560831ae49e4d789517a5bad0c3494c",
}


async def upgrade(session):
    for cat_id, name, code, val_type, has_interest, has_maturity in SUBCATEGORIES:
        sub_id = SUBCATEGORY_UUIDS.get(code)
        if not sub_id:
            continue

        if val_type == "UNIT_BASED":
            desc = "This category calculates assets dynamically based on quantity/weight held. The initial invested value will be computed automatically as (Units × Price per unit).\n\nLogging different Invested and Current Values will record a revaluation adjustments history transaction in the ledger."
        elif has_interest:
            desc = "This category tracks interest-bearing deposits with maturity details. You supply the initial invested value and current value directly.\n\nLogging different Invested and Current Values will record a revaluation adjustments history transaction in the ledger."
        else:
            desc = "This category tracks flat balance accounts. You supply the initial invested value and current value directly.\n\nLogging different Invested and Current Values will record a revaluation adjustments history transaction in the ledger."

        result = await session.execute(select(AssetSubcategoryModel).where(AssetSubcategoryModel.code == code))
        existing = result.scalars().first()

        if existing:
            old_id = existing.id
            if old_id != sub_id:
                print(f"Updating subcategory ID for {code}: {old_id} -> {sub_id}")
                # 1. Temporarily rename old code and name to avoid unique constraint violations
                existing.code = code + "_old"
                existing.name = existing.name + " (Old)"
                await session.flush()

                # 2. Create new subcategory with correct UUID ID
                new_sub = AssetSubcategoryModel(
                    id=sub_id,
                    category_id=cat_id,
                    name=name,
                    code=code,
                    description=desc,
                    valuation_type=val_type,
                    has_interest=has_interest,
                    has_maturity=has_maturity,
                )
                session.add(new_sub)
                await session.flush()

                # 3. Update references in asset table
                await session.execute(
                    text("UPDATE asset SET subcategory_id = :new_id WHERE subcategory_id = :old_id"),
                    {"new_id": sub_id, "old_id": old_id},
                )

                # 4. Delete old subcategory record
                await session.execute(text("DELETE FROM asset_subcategory WHERE id = :old_id"), {"old_id": old_id})
            else:
                print(f"Updating subcategory: {code}")
                existing.category_id = cat_id
                existing.name = name
                existing.description = desc
                existing.valuation_type = val_type
                existing.has_interest = has_interest
                existing.has_maturity = has_maturity
        else:
            print(f"Creating subcategory: {code}")
            new_sub = AssetSubcategoryModel(
                id=sub_id,
                category_id=cat_id,
                name=name,
                code=code,
                description=desc,
                valuation_type=val_type,
                has_interest=has_interest,
                has_maturity=has_maturity,
            )
            session.add(new_sub)
