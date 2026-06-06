"""add_asset_subcategory_table

Revision ID: 9a00a9672c95
Revises: cf75512f371a
Create Date: 2026-06-06 13:16:33.926397

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a00a9672c95'
down_revision: Union[str, Sequence[str], None] = 'cf75512f371a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


import uuid

def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('asset_subcategory',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('category_id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('code', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('valuation_type', sa.String(), nullable=False),
    sa.Column('has_interest', sa.Boolean(), nullable=False),
    sa.Column('has_maturity', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['asset_category.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_asset_subcategory_code'), 'asset_subcategory', ['code'], unique=True)
    op.create_index(op.f('ix_asset_subcategory_category_id'), 'asset_subcategory', ['category_id'], unique=False)

    # Add columns to asset table
    op.add_column('asset', sa.Column('subcategory_id', sa.String(), nullable=True))
    op.add_column('asset', sa.Column('interest_rate', sa.Float(), nullable=True))
    op.add_column('asset', sa.Column('interest_compounding', sa.String(), nullable=True))
    op.add_column('asset', sa.Column('maturity_date', sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key('fk_asset_subcategory', 'asset', 'asset_subcategory', ['subcategory_id'], ['id'], ondelete='RESTRICT')
    op.create_index(op.f('ix_asset_subcategory_id'), 'asset', ['subcategory_id'], unique=False)

    # Seed predefined subcategories
    # Categories: EQUITY (5d287bc128794c4fae855f75e7a9e6b1), DEBT (2f4a47da2f174780a424e7561a09d3b4),
    # REAL_ESTATE (e439bb7f10b741008d5b88c426f6e522), COMMODITIES (a434c382103b417e914e9f7823f6e111),
    # CASH_BANK (c831c382123b417e914e9f7823f6e222)
    
    subcategories = [
        # EQUITY
        ('5d287bc128794c4fae855f75e7a9e6b1', 'Stock', 'STOCK', 'UNIT_BASED', False, False),
        ('5d287bc128794c4fae855f75e7a9e6b1', 'Mutual Fund', 'MUTUAL_FUND', 'UNIT_BASED', False, False),
        ('5d287bc128794c4fae855f75e7a9e6b1', 'ETF', 'ETF', 'UNIT_BASED', False, False),
        ('5d287bc128794c4fae855f75e7a9e6b1', 'NPS', 'NPS_EQUITY', 'UNIT_BASED', False, True),
        ('5d287bc128794c4fae855f75e7a9e6b1', 'Other Equity', 'OTHER_EQUITY', 'UNIT_BASED', False, False),
        
        # DEBT
        ('2f4a47da2f174780a424e7561a09d3b4', 'PPF', 'PPF', 'VALUE_BASED', True, True),
        ('2f4a47da2f174780a424e7561a09d3b4', 'EPF / VPF', 'EPF_VPF', 'VALUE_BASED', True, False),
        ('2f4a47da2f174780a424e7561a09d3b4', 'NPS', 'NPS_DEBT', 'VALUE_BASED', True, True),
        ('2f4a47da2f174780a424e7561a09d3b4', 'SSY', 'SSY', 'VALUE_BASED', True, True),
        ('2f4a47da2f174780a424e7561a09d3b4', 'Govt. Savings Scheme', 'GOVT_SAVINGS', 'VALUE_BASED', True, True),
        ('2f4a47da2f174780a424e7561a09d3b4', 'Fixed Deposit', 'FIXED_DEPOSIT', 'VALUE_BASED', True, True),
        ('2f4a47da2f174780a424e7561a09d3b4', 'Recurring Deposit', 'RECURRING_DEPOSIT', 'VALUE_BASED', True, True),
        ('2f4a47da2f174780a424e7561a09d3b4', 'Bonds', 'BONDS', 'UNIT_BASED', True, True),
        ('2f4a47da2f174780a424e7561a09d3b4', 'Other Debt', 'OTHER_DEBT', 'VALUE_BASED', False, False),
        
        # REAL ESTATE
        ('e439bb7f10b741008d5b88c426f6e522', 'Residential Property', 'RESIDENTIAL', 'VALUE_BASED', False, False),
        ('e439bb7f10b741008d5b88c426f6e522', 'Commercial Property', 'COMMERCIAL', 'VALUE_BASED', False, False),
        ('e439bb7f10b741008d5b88c426f6e522', 'Plot', 'PLOT', 'VALUE_BASED', False, False),
        ('e439bb7f10b741008d5b88c426f6e522', 'REIT', 'REIT', 'UNIT_BASED', False, False),
        ('e439bb7f10b741008d5b88c426f6e522', 'Other Property', 'OTHER_PROPERTY', 'VALUE_BASED', False, False),
        
        # COMMODITIES
        ('a434c382103b417e914e9f7823f6e111', 'Physical Gold / Silver', 'PHYSICAL_GOLD_SILVER', 'UNIT_BASED', False, False),
        ('a434c382103b417e914e9f7823f6e111', 'Digital (ETF / SGB / MF)', 'DIGITAL_COMMODITIES', 'UNIT_BASED', False, False),
        ('a434c382103b417e914e9f7823f6e111', 'Sovereign Gold Bond', 'SGB', 'UNIT_BASED', True, True),
        
        # CASH / BANK
        ('c831c382123b417e914e9f7823f6e222', 'Savings Account', 'SAVINGS_ACCOUNT', 'VALUE_BASED', True, False),
        ('c831c382123b417e914e9f7823f6e222', 'Current Account', 'CURRENT_ACCOUNT', 'VALUE_BASED', False, False),
        ('c831c382123b417e914e9f7823f6e222', 'Cash in Hand', 'CASH_IN_HAND', 'VALUE_BASED', False, False),
        ('c831c382123b417e914e9f7823f6e222', 'Other Cash', 'OTHER_CASH', 'VALUE_BASED', False, False),
    ]

    for cat_id, name, code, val_type, has_interest, has_maturity in subcategories:
        sub_id = uuid.uuid4().hex
        if val_type == 'UNIT_BASED':
            desc = "This category calculates assets dynamically based on quantity/weight held. The initial invested value will be computed automatically as (Units × Price per unit).\n\nLogging different Invested and Current Values will record a revaluation adjustments history transaction in the ledger."
        elif has_interest:
            desc = "This category tracks interest-bearing deposits with maturity details. You supply the initial invested value and current value directly.\n\nLogging different Invested and Current Values will record a revaluation adjustments history transaction in the ledger."
        else:
            desc = "This category tracks flat balance accounts. You supply the initial invested value and current value directly.\n\nLogging different Invested and Current Values will record a revaluation adjustments history transaction in the ledger."
        desc_escaped = desc.replace("'", "''")
        op.execute(
            f"INSERT INTO asset_subcategory (id, category_id, name, code, description, valuation_type, has_interest, has_maturity, created_at, updated_at) "
            f"VALUES ('{sub_id}', '{cat_id}', '{name}', '{code}', '{desc_escaped}', '{val_type}', {has_interest}, {has_maturity}, NOW(), NOW())"
        )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_asset_subcategory_id'), table_name='asset')
    op.drop_constraint('fk_asset_subcategory', 'asset', type_='foreignkey')
    op.drop_column('asset', 'subcategory_id')
    op.drop_column('asset', 'interest_rate')
    op.drop_column('asset', 'interest_compounding')
    op.drop_column('asset', 'maturity_date')
    
    op.drop_index(op.f('ix_asset_subcategory_code'), table_name='asset_subcategory')
    op.drop_index(op.f('ix_asset_subcategory_category_id'), table_name='asset_subcategory')
    op.drop_table('asset_subcategory')
