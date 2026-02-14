"""Rename MonthYear to Period

Revision ID: 495db70b428b
Revises: 14098a210fb7
Create Date: 2026-02-14 10:35:19.176908

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '495db70b428b'
down_revision: Union[str, Sequence[str], None] = '14098a210fb7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop constraints referencing the old names
    op.drop_constraint(op.f('uq_account_date_detail'), 'spending_account_entries', type_='unique')
    op.drop_constraint(op.f('spending_account_entries_date_detail_id_fkey'), 'spending_account_entries', type_='foreignkey')
    op.drop_index(op.f('ix_spending_account_entries_date_detail_id'), table_name='spending_account_entries')
    
    # Rename the table
    op.rename_table('month_years', 'period')
    
    # Rename indexes on the renamed table
    op.execute('ALTER INDEX ix_month_years_month RENAME TO ix_period_month')
    op.execute('ALTER INDEX ix_month_years_year RENAME TO ix_period_year')
    
    # Rename the column
    op.execute('ALTER TABLE spending_account_entries RENAME COLUMN date_detail_id TO period_id')
    
    # Create new constraints with updated names
    op.create_index(op.f('ix_spending_account_entries_period_id'), 'spending_account_entries', ['period_id'], unique=False)
    op.create_unique_constraint('uq_account_period', 'spending_account_entries', ['account_id', 'period_id'])
    op.create_foreign_key(None, 'spending_account_entries', 'period', ['period_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f('uq_account_period'), 'spending_account_entries', type_='unique')
    op.drop_constraint(op.f('spending_account_entries_period_id_fkey'), 'spending_account_entries', type_='foreignkey')
    op.drop_index(op.f('ix_spending_account_entries_period_id'), table_name='spending_account_entries')
    
    # Rename table back
    op.rename_table('period', 'month_years')
    
    # Rename indexes back
    op.execute('ALTER INDEX ix_period_month RENAME TO ix_month_years_month')
    op.execute('ALTER INDEX ix_period_year RENAME TO ix_month_years_year')

    # Rename the column
    op.execute('ALTER TABLE spending_account_entries RENAME COLUMN period_id TO date_detail_id')
    
    # Recreate old constraints
    op.create_index(op.f('ix_spending_account_entries_date_detail_id'), 'spending_account_entries', ['date_detail_id'], unique=False)
    op.create_unique_constraint('uq_account_date_detail', 'spending_account_entries', ['account_id', 'date_detail_id'])
    op.create_foreign_key(None, 'spending_account_entries', 'month_years', ['date_detail_id'], ['id'], ondelete='CASCADE')
