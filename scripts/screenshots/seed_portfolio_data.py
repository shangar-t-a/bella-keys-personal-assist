"""Demo data seeder for Bella Keys — pushes portfolio-quality data directly to PostgreSQL.

Idempotent: checks by name/code before inserting; never deletes existing records.
Run from scripts/screenshots/ with the EMS database reachable.

Usage:
    uv run seed_demo_data.py

Env var override:
    EMS_PG_DATABASE_URL   postgresql+asyncpg://user:pass@host/db
"""

import asyncio
import os
import sys
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

# Load .env from the EMS service directory so DATABASE_URL is available
_SCRIPT_DIR = Path(__file__).parent
_REPO_ROOT = _SCRIPT_DIR.parent.parent
_EMS_ENV = _REPO_ROOT / "services" / "expense-manager-service" / ".env"
if _EMS_ENV.exists():
    load_dotenv(_EMS_ENV)

load_dotenv()


def _db_url() -> str:
    url = os.getenv("EMS_PG_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not url:
        sys.exit(
            "[seed] ERROR: set EMS_PG_DATABASE_URL or DATABASE_URL before running.\n"
            "  Example: EMS_PG_DATABASE_URL=postgresql+asyncpg://ems_user:pass@localhost:5432/expense_manager_dev"
        )
    # Ensure asyncpg driver
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def _uid() -> str:
    return uuid.uuid4().hex


def _dt(days_ago: int = 0, months_ago: int = 0) -> datetime:
    d = datetime.now(UTC) - timedelta(days=days_ago + months_ago * 30)
    return d.replace(hour=10, minute=0, second=0, microsecond=0)


async def _upsert_period(session, month: int, year: int) -> str:
    res = await session.execute(
        text("SELECT id FROM period WHERE month = :m AND year = :y"),
        {"m": month, "y": year},
    )
    row = res.fetchone()
    if row:
        return row[0]
    pid = _uid()
    await session.execute(
        text(
            "INSERT INTO period (id, month, year, created_at, updated_at) "
            "VALUES (:id, :m, :y, NOW(), NOW())"
        ),
        {"id": pid, "m": month, "y": year},
    )
    return pid


async def _upsert_account(session, name: str) -> str:
    res = await session.execute(
        text("SELECT id FROM account WHERE account_name = :n"),
        {"n": name.upper()},
    )
    row = res.fetchone()
    if row:
        return row[0]
    aid = _uid()
    await session.execute(
        text("INSERT INTO account (id, account_name, created_at, updated_at) VALUES (:id, :n, NOW(), NOW())"),
        {"id": aid, "n": name.upper()},
    )
    return aid


async def seed_spending(session) -> None:
    print("[seed] Spending accounts + entries...")

    # Account definitions: (name, base_balance, base_credit_ratio)
    accounts = [
        ("HDFC Salary",  120_000, 0.70),
        ("ICICI Savings", 45_000, 0.30),
        ("Zerodha",       82_000, 0.15),
    ]

    # 12 months Jul 2024 -> Jun 2025
    months = [(7 + i - 1) % 12 + 1 for i in range(12)]
    years  = [2024 if (7 + i - 1) < 12 else 2025 for i in range(12)]
    # Dec/Jan spend spike factor
    spike = {12: 1.20, 1: 1.15, 11: 1.05}

    for acc_name, base_bal, credit_ratio in accounts:
        acc_id = await _upsert_account(session, acc_name)
        running_bal = float(base_bal)

        for i, (m, y) in enumerate(zip(months, years)):
            period_id = await _upsert_period(session, m, y)

            res = await session.execute(
                text("SELECT id FROM spending_entry WHERE account_id = :a AND period_id = :p"),
                {"a": acc_id, "p": period_id},
            )
            if res.fetchone():
                continue

            factor = spike.get(m, 1.0) * (1 + i * 0.008)  # slight growth
            spend = round(base_bal * credit_ratio * factor, 2)
            current_bal = round(running_bal - spend * 0.6, 2)
            credit = round(spend, 2)
            starting_bal = round(running_bal, 2)
            running_bal = current_bal + base_bal * 0.05  # small month-end top-up

            await session.execute(
                text(
                    "INSERT INTO spending_entry "
                    "(id, account_id, period_id, starting_balance, current_balance, current_credit, "
                    "created_at, updated_at) "
                    "VALUES (:id, :a, :p, :sb, :cb, :cc, NOW(), NOW())"
                ),
                {
                    "id": _uid(), "a": acc_id, "p": period_id,
                    "sb": starting_bal, "cb": current_bal, "cc": credit,
                },
            )

    await session.commit()
    print("[seed]   OK Spending done")


async def seed_budget(session) -> None:
    print("[seed] Monthly budget (categories + expense items + summaries)...")

    # Ensure monthly categories exist
    spending_cats = [
        ("Rent & Housing", "spending"),
        ("Groceries",      "spending"),
        ("Utilities",      "spending"),
        ("Transport",      "spending"),
        ("Entertainment",  "spending"),
        ("Health",         "spending"),
        ("Misc",           "spending"),
    ]
    saving_cats = [
        ("Investments",  "saving"),
        ("Emergency",    "saving"),
        ("Goals",        "saving"),
    ]
    all_cats = spending_cats + saving_cats

    cat_ids: dict[str, str] = {}
    for cat_name, l1 in all_cats:
        res = await session.execute(
            text("SELECT id FROM monthly_category WHERE name = :n AND category_l1 = :l"),
            {"n": cat_name, "l": l1},
        )
        row = res.fetchone()
        if row:
            cat_ids[cat_name] = row[0]
        else:
            cid = _uid()
            await session.execute(
                text(
                    "INSERT INTO monthly_category (id, name, category_l1, created_at) "
                    "VALUES (:id, :n, :l, NOW())"
                ),
                {"id": cid, "n": cat_name, "l": l1},
            )
            cat_ids[cat_name] = cid

    # 12 months of budget data
    months = [(7 + i - 1) % 12 + 1 for i in range(12)]
    years  = [2024 if (7 + i - 1) < 12 else 2025 for i in range(12)]

    # Monthly expense template: (name, amount, category, l1, is_recurring, status)
    expense_template = [
        ("House Rent",           22_000, "Rent & Housing",  "spending", True,  "settled"),
        ("Electricity Bill",      2_500, "Utilities",       "spending", True,  "settled"),
        ("Internet & Phone",      1_200, "Utilities",       "spending", True,  "settled"),
        ("Groceries & Kitchen",   8_500, "Groceries",       "spending", True,  "settled"),
        ("Zomato / Swiggy",       3_200, "Entertainment",   "spending", False, "settled"),
        ("OTT Subscriptions",       999, "Entertainment",   "spending", True,  "settled"),
        ("Petrol / Cab",          3_800, "Transport",       "spending", True,  "settled"),
        ("Gym Membership",        1_500, "Health",          "spending", True,  "settled"),
        ("Medicine & Health",     1_200, "Health",          "spending", False, "pending"),
        ("Nifty 50 SIP",         10_000, "Investments",     "saving",   True,  "settled"),
        ("PPF Deposit",          12_500, "Investments",     "saving",   True,  "settled"),
        ("Digital Gold SIP",      2_000, "Goals",           "saving",   True,  "settled"),
        ("Emergency Top-up",      5_000, "Emergency",       "saving",   False, "settled"),
        ("Misc Expenses",         2_500, "Misc",            "spending", False, "pending"),
    ]

    for m, y in zip(months, years):
        period_id = await _upsert_period(session, m, y)

        # Summary (salary)
        res = await session.execute(
            text("SELECT id FROM monthly_summary WHERE period_id = :p"),
            {"p": period_id},
        )
        if not res.fetchone():
            await session.execute(
                text(
                    "INSERT INTO monthly_summary (id, period_id, salary, created_at, updated_at) "
                    "VALUES (:id, :p, :s, NOW(), NOW())"
                ),
                {"id": _uid(), "p": period_id, "s": 135_000.0},
            )

        # Expense items
        res = await session.execute(
            text("SELECT COUNT(*) FROM monthly_expense_item WHERE period_id = :p"),
            {"p": period_id},
        )
        if res.scalar() > 0:
            continue

        for name, amount, cat_l2, l1, recurring, status in expense_template:
            # Small random ±5% variance for realism
            variance = 1 + (hash(f"{name}{m}{y}") % 11 - 5) / 100
            final_amount = round(amount * variance, 2)
            await session.execute(
                text(
                    "INSERT INTO monthly_expense_item "
                    "(id, period_id, name, amount, status, category_l1, category_l2, "
                    "is_recurring, created_at, updated_at) "
                    "VALUES (:id, :p, :n, :a, :s, :l1, :l2, :r, NOW(), NOW())"
                ),
                {
                    "id": _uid(), "p": period_id, "n": name, "a": final_amount,
                    "s": status, "l1": l1, "l2": cat_l2, "r": recurring,
                },
            )

    await session.commit()
    print("[seed]   OK Budget done")


async def seed_savings(session) -> None:
    print("[seed] Savings envelopes + transactions...")

    # Use HDFC Salary account for savings buckets
    acc_id = await _upsert_account(session, "HDFC Salary")

    buckets = [
        ("Emergency Fund",      240_000, 300_000),
        ("Europe Trip 2025",     85_000, 150_000),
        ("New Laptop",           42_000, 120_000),
        ("Wedding Anniversary",  28_000,  50_000),
        ("Car Down Payment",    110_000, 500_000),
    ]

    bucket_ids: dict[str, str] = {}
    for b_name, allocated, target in buckets:
        res = await session.execute(
            text("SELECT id FROM savings_bucket WHERE account_id = :a AND name = :n"),
            {"a": acc_id, "n": b_name},
        )
        row = res.fetchone()
        if row:
            bucket_ids[b_name] = row[0]
        else:
            bid = _uid()
            await session.execute(
                text(
                    "INSERT INTO savings_bucket "
                    "(id, account_id, name, allocated_amount, target_amount, created_at, updated_at) "
                    "VALUES (:id, :a, :n, :al, :tg, NOW(), NOW())"
                ),
                {"id": bid, "a": acc_id, "n": b_name, "al": float(allocated), "tg": float(target)},
            )
            bucket_ids[b_name] = bid

    # Seed deposit transactions for each bucket (spread over 12 months)
    for b_name, allocated, _ in buckets:
        bid = bucket_ids[b_name]
        monthly_dep = round(allocated / 12, 2)
        for i in range(12):
            tx_date = _dt(months_ago=11 - i)
            res = await session.execute(
                text(
                    "SELECT id FROM savings_bucket_transaction "
                    "WHERE destination_bucket_id = :b AND transaction_type = 'deposit' "
                    "AND DATE(transaction_date) = DATE(:d)"
                ),
                {"b": bid, "d": tx_date},
            )
            if res.fetchone():
                continue
            await session.execute(
                text(
                    "INSERT INTO savings_bucket_transaction "
                    "(id, account_id, source_bucket_id, destination_bucket_id, amount, "
                    "transaction_type, description, transaction_date, is_cancelled, created_at) "
                    "VALUES (:id, :a, NULL, :b, :amt, 'deposit', :desc, :d, FALSE, NOW())"
                ),
                {
                    "id": _uid(), "a": acc_id, "b": bid, "amt": monthly_dep,
                    "desc": f"Monthly deposit — {b_name}",
                    "d": tx_date,
                },
            )

    await session.commit()
    print("[seed]   OK Savings done")


async def seed_assets(session) -> None:
    print("[seed] Assets + transactions...")

    default_asset_cats = [
        ("EQUITY", "Equity", "Stocks, Mutual Funds, ETFs"),
        ("DEBT", "Debt", "Fixed Deposits, PPF, Bonds, EPF"),
        ("REAL_ESTATE", "Real Estate", "Land, Residential/Commercial Properties"),
        ("COMMODITIES", "Commodities", "Physical/Digital Gold, Silver"),
        ("CASH_BANK", "Cash / Bank", "Savings accounts, Cash"),
    ]
    actual_cat = {}
    for code, name, desc in default_asset_cats:
        res = await session.execute(
            text("SELECT id FROM asset_category WHERE code = :c"), {"c": code}
        )
        row = res.fetchone()
        if row:
            actual_cat[code] = row[0]
        else:
            cid = _uid()
            await session.execute(
                text(
                    "INSERT INTO asset_category (id, name, code, description, created_at, updated_at) "
                    "VALUES (:id, :n, :c, :d, NOW(), NOW())"
                ),
                {"id": cid, "n": name, "c": code, "d": desc},
            )
            actual_cat[code] = cid

    # Fetch subcategory IDs
    sub_res = await session.execute(text("SELECT code, id FROM asset_subcategory"))
    sub_by_code = {r[0]: r[1] for r in sub_res.fetchall()}

    assets = [
        # (name, cat_code, sub_code, invested, current, interest_rate, compounding, maturity_days)
        ("Nifty 50 Index Fund",  "EQUITY",      "MF_INDEX",  500_000, 642_000, None,   None,       None),
        ("HDFC Mid-Cap Fund",    "EQUITY",      "MF_ACTIVE",  200_000, 261_000, None,   None,       None),
        ("Infosys Shares",       "EQUITY",      "STOCKS",    150_000, 189_000, None,   None,       None),
        ("PPF Account",          "DEBT",        "PPF",       300_000, 328_500, 7.1,   "YEARLY",   365 * 8),
        ("SBI FD 5yr",           "DEBT",        "BANK_FD",   100_000, 109_200, 7.5,   "QUARTERLY", 365 * 3),
        ("Digital Gold",         "COMMODITIES", "DIGITAL_GOLD", 80_000, 112_000, None, None,       None),
        ("Ancestral Plot",       "REAL_ESTATE", "LAND",      800_000, 1_200_000, None, None,       None),
        ("HDFC Savings Account", "CASH_BANK",   "SAVINGS_AC", 120_000, 120_000, 3.5,  "QUARTERLY", None),
    ]

    asset_ids: dict[str, str] = {}
    for (name, cat_code, sub_code, invested, current, irate, comp, mat_days) in assets:
        res = await session.execute(
            text("SELECT id FROM asset WHERE name = :n"), {"n": name}
        )
        row = res.fetchone()
        if row:
            asset_ids[name] = row[0]
            # Update values to current
            await session.execute(
                text(
                    "UPDATE asset SET invested_value = :iv, current_value = :cv, updated_at = NOW() "
                    "WHERE id = :id"
                ),
                {"iv": float(invested), "cv": float(current), "id": row[0]},
            )
            continue

        aid = _uid()
        asset_ids[name] = aid
        maturity_date = (_dt() + timedelta(days=mat_days)) if mat_days else None
        await session.execute(
            text(
                "INSERT INTO asset "
                "(id, category_id, name, subcategory_id, invested_value, current_value, "
                "interest_rate, interest_compounding, maturity_date, notes, created_at, updated_at) "
                "VALUES (:id, :cat, :name, :sub, :iv, :cv, :ir, :ic, :md, :notes, NOW(), NOW())"
            ),
            {
                "id": aid,
                "cat": actual_cat.get(cat_code, _uid()),
                "name": name,
                "sub": sub_by_code.get(sub_code),
                "iv": float(invested),
                "cv": float(current),
                "ir": float(irate) if irate else None,
                "ic": comp,
                "md": maturity_date,
                "notes": None,
            },
        )

    # Asset transactions: programmatically generated to produce a beautiful smooth curve
    tx_schedule = {}

    # 1. Nifty 50 Index Fund (Invested: 500k, Current: 642k)
    nifty_txs = []
    for m in range(20, -1, -1):
        nifty_txs.append((m, 25_000))
    nifty_revals = [
        (18, "REVALUE", 52_000),
        (15, "REVALUE", 138_000),
        (12, "REVALUE", 235_000),
        (9, "REVALUE", 345_000),
        (6, "REVALUE", 460_000),
        (3, "REVALUE", 575_000),
        (0, "REVALUE", 642_000),
    ]
    nifty_txs.extend(nifty_revals)
    tx_schedule["Nifty 50 Index Fund"] = nifty_txs

    # 2. HDFC Mid-Cap Fund (Invested: 200k, Current: 261k)
    hdfc_txs = []
    for m in range(20, -1, -1):
        hdfc_txs.append((m, 10_000))
    hdfc_revals = [
        (18, "REVALUE", 21_000),
        (15, "REVALUE", 55_000),
        (12, "REVALUE", 95_000),
        (9, "REVALUE", 138_000),
        (6, "REVALUE", 185_000),
        (3, "REVALUE", 232_000),
        (0, "REVALUE", 261_000),
    ]
    hdfc_txs.extend(hdfc_revals)
    tx_schedule["HDFC Mid-Cap Fund"] = hdfc_txs

    # 3. Infosys Shares (Invested: 150k, Current: 189k)
    infy_txs = [(18, 150_000)]
    infy_revals = [
        (15, "REVALUE", 155_000),
        (12, "REVALUE", 162_000),
        (9, "REVALUE", 170_000),
        (6, "REVALUE", 178_000),
        (3, "REVALUE", 184_000),
        (0, "REVALUE", 189_000),
    ]
    infy_txs.extend(infy_revals)
    tx_schedule["Infosys Shares"] = infy_txs

    # 4. PPF Account (Invested: 300k, Current: 328.5k)
    ppf_txs = []
    for m in range(24, -1, -1):
        ppf_txs.append((m, 12_500))
    ppf_revals = [
        (21, "REVALUE", 38_500),
        (18, "REVALUE", 78_000),
        (15, "REVALUE", 118_500),
        (12, "REVALUE", 160_000),
        (9, "REVALUE", 201_500),
        (6, "REVALUE", 243_000),
        (3, "REVALUE", 285_500),
        (0, "REVALUE", 328_500),
    ]
    ppf_txs.extend(ppf_revals)
    tx_schedule["PPF Account"] = ppf_txs

    # 5. SBI FD 5yr (Invested: 100k, Current: 109.2k)
    sbi_txs = [(18, 100_000)]
    sbi_revals = [
        (15, "REVALUE", 101_800),
        (12, "REVALUE", 103_600),
        (9, "REVALUE", 105_400),
        (6, "REVALUE", 107_200),
        (3, "REVALUE", 108_500),
        (0, "REVALUE", 109_200),
    ]
    sbi_txs.extend(sbi_revals)
    tx_schedule["SBI FD 5yr"] = sbi_txs

    # 6. Digital Gold (Invested: 80k, Current: 112k)
    gold_txs = []
    for m in range(18, -1, -1):
        gold_txs.append((m, 4_444.44))
    gold_revals = [
        (15, "REVALUE", 14_000),
        (12, "REVALUE", 29_000),
        (9, "REVALUE", 46_000),
        (6, "REVALUE", 65_000),
        (3, "REVALUE", 87_000),
        (0, "REVALUE", 112_000),
    ]
    gold_txs.extend(gold_revals)
    tx_schedule["Digital Gold"] = gold_txs

    # 7. Ancestral Plot (Invested: 800k, Current: 1.2M)
    plot_txs = [
        (24, 800_000),
        (22, "ANCILLARY_FEE", 64_000),
        (18, "REVALUE", 900_000),
        (16, "IMPROVEMENT", 85_000),
        (12, "REVALUE", 1_000_000),
        (10, "CAPITALIZED_INTEREST", 42_000),
        (6, "REVALUE", 1_100_000),
        (0, "REVALUE", 1_200_000),
    ]
    tx_schedule["Ancestral Plot"] = plot_txs

    # 8. HDFC Savings Account
    tx_schedule["HDFC Savings Account"] = [(12, 120_000)]

    for asset_name, txs in tx_schedule.items():
        aid = asset_ids.get(asset_name)
        if not aid:
            continue
        for tx in txs:
            months_ago = tx[0]
            tx_date = _dt(months_ago=months_ago)
            if len(tx) == 3:
                tx_type = tx[1]
                amount = float(tx[2])
                units = None
                ppu = None
            else:
                amount = float(tx[1])
                tx_type = "BUY"
                units = None
                ppu = None

            res = await session.execute(
                text(
                    "SELECT id FROM asset_transaction "
                    "WHERE asset_id = :a AND transaction_type = :t AND DATE(transaction_date) = DATE(:d)"
                ),
                {"a": aid, "t": tx_type, "d": tx_date},
            )
            if res.fetchone():
                continue

            await session.execute(
                text(
                    "INSERT INTO asset_transaction "
                    "(id, asset_id, transaction_type, amount, units, price_per_unit, "
                    "transaction_date, description, created_at) "
                    "VALUES (:id, :a, :t, :amt, :u, :ppu, :d, :desc, NOW())"
                ),
                {
                    "id": _uid(), "a": aid, "t": tx_type, "amt": amount,
                    "u": units, "ppu": ppu, "d": tx_date,
                    "desc": f"Demo seed — {tx_type.lower()}",
                },
            )

    await session.commit()
    print("[seed]   OK Assets done")


async def seed_liabilities(session) -> None:
    print("[seed] Liabilities + repayment history...")

    default_liability_cats = [
        ("SECURED_LOAN", "Secured Loans", "Loans backed by collateral like home, vehicle"),
        ("UNSECURED_LOAN", "Unsecured Loans", "Loans with no collateral like personal, education loans"),
        ("REVOLVING_CREDIT", "Revolving Credit", "Lines of credit like credit cards"),
        ("OTHER", "Other Liabilities", "Family loans, hand loans, or general liabilities"),
    ]
    lib_cats = {}
    for code, name, desc in default_liability_cats:
        res = await session.execute(
            text("SELECT id FROM liability_category WHERE code = :c"), {"c": code}
        )
        row = res.fetchone()
        if row:
            lib_cats[code] = row[0]
        else:
            cid = _uid()
            await session.execute(
                text(
                    "INSERT INTO liability_category (id, name, code, description, created_at, updated_at) "
                    "VALUES (:id, :n, :c, :d, NOW(), NOW())"
                ),
                {"id": cid, "n": name, "c": code, "d": desc},
            )
            lib_cats[code] = cid

    res = await session.execute(text("SELECT code, id FROM liability_subcategory"))
    lib_subs = {r[0]: r[1] for r in res.fetchall()}

    liabilities = [
        # (name, cat_code, sub_code, original, current, rate, compounding, emi, emi_start_months_ago, maturity_years)
        (
            "Home Loan — SBI", "SECURED_LOAN", "HOME_LOAN",
            3_500_000, 2_940_000, 8.5, "MONTHLY", 28_500, 24, 20,
        ),
        (
            "Car Loan — HDFC", "SECURED_LOAN", "VEHICLE_LOAN",
            650_000, 320_000, 9.0, "MONTHLY", 12_800, 18, 5,
        ),
    ]

    for (name, cat_code, sub_code, original, current, rate, comp, emi, emi_months_ago, mat_years) in liabilities:
        res = await session.execute(
            text("SELECT id FROM liability WHERE name = :n"), {"n": name}
        )
        row = res.fetchone()

        cat_id = lib_cats.get(cat_code)
        sub_id = lib_subs.get(sub_code)
        emi_start = _dt(months_ago=emi_months_ago)
        maturity_date = _dt() + timedelta(days=365 * mat_years)

        if row:
            lid = row[0]
            await session.execute(
                text(
                    "UPDATE liability SET current_value = :cv, updated_at = NOW() WHERE id = :id"
                ),
                {"cv": float(current), "id": lid},
            )
        else:
            lid = _uid()
            await session.execute(
                text(
                    "INSERT INTO liability "
                    "(id, category_id, name, subcategory_id, original_value, current_value, "
                    "interest_rate, interest_compounding, emi_amount, emi_start_date, maturity_date, "
                    "notes, created_at, updated_at) "
                    "VALUES (:id, :cat, :name, :sub, :ov, :cv, :ir, :ic, :emi, :es, :md, NULL, NOW(), NOW())"
                ),
                {
                    "id": lid, "cat": cat_id, "name": name, "sub": sub_id,
                    "ov": float(original), "cv": float(current),
                    "ir": float(rate), "ic": comp, "emi": float(emi),
                    "es": emi_start, "md": maturity_date,
                },
            )

        # Monthly REPAY transactions for the last emi_months_ago months
        for i in range(emi_months_ago):
            tx_date = _dt(months_ago=emi_months_ago - 1 - i)
            res = await session.execute(
                text(
                    "SELECT id FROM liability_transaction "
                    "WHERE liability_id = :l AND transaction_type = 'REPAY' "
                    "AND DATE(transaction_date) = DATE(:d)"
                ),
                {"l": lid, "d": tx_date},
            )
            if res.fetchone():
                continue
            await session.execute(
                text(
                    "INSERT INTO liability_transaction "
                    "(id, liability_id, transaction_type, amount, transaction_date, description, created_at) "
                    "VALUES (:id, :l, 'REPAY', :amt, :d, :desc, NOW())"
                ),
                {
                    "id": _uid(), "l": lid, "amt": float(emi),
                    "d": tx_date, "desc": f"Monthly EMI — {name}",
                },
            )

    await session.commit()
    print("[seed]   OK Liabilities done")


async def seed_backups(session) -> None:
    print("[seed] Backup snapshots...")
    import json
    backup_dir = os.path.expanduser(os.path.join("~", ".bella-keys", "backups"))
    os.makedirs(backup_dir, exist_ok=True)

    existing_files = [f for f in os.listdir(backup_dir) if f.endswith(".json")]
    if existing_files:
        print(f"[seed]   OK {len(existing_files)} existing backup snapshot(s) found.")
        return

    timestamp_str = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    filename = f"ems_backup_{timestamp_str}.json"
    file_path = os.path.join(backup_dir, filename)

    tables = [
        "account", "period", "monthly_category", "monthly_summary", "monthly_expense_item",
        "savings_bucket", "savings_bucket_transaction", "asset_category", "asset_subcategory",
        "asset", "asset_transaction", "liability_category", "liability_subcategory",
        "liability", "liability_transaction", "spending_entry"
    ]

    table_data = {}
    record_counts = {}
    for table_name in tables:
        res = await session.execute(text(f"SELECT * FROM {table_name}"))
        keys = res.keys()
        rows = res.fetchall()
        serialized_rows = []
        for r in rows:
            row_dict = {}
            for col_name, val in zip(keys, r):
                if isinstance(val, datetime):
                    row_dict[col_name] = val.isoformat()
                else:
                    row_dict[col_name] = val
            serialized_rows.append(row_dict)
        table_data[table_name] = serialized_rows
        record_counts[table_name] = len(serialized_rows)

    payload = {
        "metadata": {
            "version": "1.0",
            "service": "expense_manager",
            "exported_at": datetime.now(UTC).isoformat(),
            "record_counts": record_counts,
            "total_records": sum(record_counts.values()),
        },
        "tables": table_data,
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"[seed]   OK Initial backup snapshot created: {filename}")


async def clean_database(session, db_url: str | None = None) -> None:
    url = db_url or _db_url()
    db_name = url.rsplit("/", 1)[-1].split("?")[0]
    app_env = os.getenv("APP_ENV", "dev").lower()

    if app_env == "prod" or not (db_name.endswith("_dev") or db_name.endswith("_test")):
        raise RuntimeError(
            f"[seed] SAFETY ERROR: Refusing to clean database '{db_name}' in environment '{app_env}'. "
            "Target database must end with '_dev' or '_test' and APP_ENV must not be 'prod'."
        )

    print(f"[seed] Cleaning/wiping development database tables in '{db_name}'...")
    tables = [
        "spending_entry",
        "savings_bucket_transaction",
        "savings_bucket",
        "monthly_expense_item",
        "monthly_summary",
        "monthly_category",
        "asset_transaction",
        "asset",
        "liability_transaction",
        "liability",
        "account",
        "period",
    ]
    # We do a single query to truncate all to avoid FK issues
    table_list = ", ".join(tables)
    try:
        await session.execute(text(f"TRUNCATE TABLE {table_list} CASCADE"))
        await session.commit()
        print("[seed]   OK Wiped tables successfully.")
    except Exception as e:
        print(f"[seed]   [WARN] Failed to truncate tables: {e}")
        await session.rollback()


async def main() -> None:
    url = _db_url()
    print("[seed] Connecting to database...")
    engine = create_async_engine(url, echo=False)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async with session_maker() as session:
        await clean_database(session, db_url=url)
        await seed_spending(session)
        await seed_budget(session)
        await seed_savings(session)
        await seed_assets(session)
        await seed_liabilities(session)
        await seed_backups(session)

    await engine.dispose()
    print("\n[seed] OK All portfolio workflow data seeded successfully.")


if __name__ == "__main__":
    asyncio.run(main())
