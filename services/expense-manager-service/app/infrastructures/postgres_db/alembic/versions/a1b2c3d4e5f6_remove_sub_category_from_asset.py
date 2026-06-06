"""remove_sub_category_from_asset

Revision ID: a1b2c3d4e5f6
Revises: 9a00a9672c95
Create Date: 2026-06-06 17:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '9a00a9672c95'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop the legacy sub_category column from the asset table."""
    op.drop_column('asset', 'sub_category')


def downgrade() -> None:
    """Re-add the sub_category column (nullable, for rollback only)."""
    op.add_column('asset', sa.Column('sub_category', sa.String(), nullable=True))
