"""Add monthly planner tables

Revision ID: b73d1f3e4c21
Revises: a7a0efd1fc61
Create Date: 2026-05-05 23:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b73d1f3e4c21'
down_revision: Union[str, Sequence[str], None] = 'a7a0efd1fc61'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # monthly_category
    op.create_table(
        'monthly_category',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('category_l1', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'category_l1', name='uq_monthly_category_name_l1')
    )

    # monthly_summary
    op.create_table(
        'monthly_summary',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('period_id', sa.String(), nullable=False),
        sa.Column('salary', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['period_id'], ['period.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('period_id', name='uq_monthly_summary_period')
    )
    op.create_index(op.f('ix_monthly_summary_period_id'), 'monthly_summary', ['period_id'], unique=False)

    # monthly_expense_item
    op.create_table(
        'monthly_expense_item',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('period_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('category_l1', sa.String(), nullable=False),
        sa.Column('category_l2', sa.String(), nullable=False),
        sa.Column('is_recurring', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['period_id'], ['period.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_monthly_expense_item_period_id'), 'monthly_expense_item', ['period_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_monthly_expense_item_period_id'), table_name='monthly_expense_item')
    op.drop_table('monthly_expense_item')
    op.drop_index(op.f('ix_monthly_summary_period_id'), table_name='monthly_summary')
    op.drop_table('monthly_summary')
    op.drop_table('monthly_category')
