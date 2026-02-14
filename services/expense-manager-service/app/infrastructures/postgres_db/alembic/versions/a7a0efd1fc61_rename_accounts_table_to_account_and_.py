"""Rename accounts table to account and spending account entried to spending entry

Revision ID: a7a0efd1fc61
Revises: 495db70b428b
Create Date: 2026-02-14 12:13:00.855519

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a7a0efd1fc61'
down_revision: Union[str, Sequence[str], None] = '495db70b428b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename constraint first (before table rename)
    op.drop_constraint('uq_month_year', 'period', type_='unique')
    op.create_unique_constraint('uq_period', 'period', ['month', 'year'])
    
    # Drop foreign keys with old table names
    op.drop_constraint('spending_account_entries_account_id_fkey', 'spending_account_entries', type_='foreignkey')
    op.drop_constraint('spending_account_entries_period_id_fkey', 'spending_account_entries', type_='foreignkey')
    
    # Rename tables
    op.rename_table('accounts', 'account')
    op.rename_table('spending_account_entries', 'spending_entry')
    
    # Recreate foreign keys with new names
    op.create_foreign_key('spending_entry_account_id_fkey', 'spending_entry', 'account', ['account_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('spending_entry_period_id_fkey', 'spending_entry', 'period', ['period_id'], ['id'], ondelete='CASCADE')
    
    # Rename indexes
    op.execute('ALTER INDEX ix_accounts_account_name RENAME TO ix_account_account_name')
    op.execute('ALTER INDEX ix_spending_account_entries_account_id RENAME TO ix_spending_entry_account_id')
    op.execute('ALTER INDEX ix_spending_account_entries_period_id RENAME TO ix_spending_entry_period_id')


def downgrade() -> None:
    """Downgrade schema."""
    # Rename constraint first (before table rename)
    op.drop_constraint('uq_period', 'period', type_='unique')
    op.create_unique_constraint('uq_month_year', 'period', ['month', 'year'])
    
    # Drop foreign keys with new table names
    op.drop_constraint('spending_entry_account_id_fkey', 'spending_entry', type_='foreignkey')
    op.drop_constraint('spending_entry_period_id_fkey', 'spending_entry', type_='foreignkey')
    
    # Rename tables
    op.rename_table('spending_entry', 'spending_account_entries')
    op.rename_table('account', 'accounts')
    
    # Recreate foreign keys with old names
    op.create_foreign_key('spending_account_entries_account_id_fkey', 'spending_account_entries', 'accounts', ['account_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('spending_account_entries_period_id_fkey', 'spending_account_entries', 'period', ['period_id'], ['id'], ondelete='CASCADE')
    
    # Rename indexes
    op.execute('ALTER INDEX ix_spending_entry_period_id RENAME TO ix_spending_account_entries_period_id')
    op.execute('ALTER INDEX ix_spending_entry_account_id RENAME TO ix_spending_account_entries_account_id')
    op.execute('ALTER INDEX ix_account_account_name RENAME TO ix_accounts_account_name')
