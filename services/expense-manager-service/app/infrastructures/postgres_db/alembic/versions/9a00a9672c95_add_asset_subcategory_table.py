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
