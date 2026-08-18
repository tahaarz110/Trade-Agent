"""تغییر FK حذف حساب از cascade به restrict برای حفظ تاریخچه معاملات

Revision ID: 494a0609b31d
Revises: 223993938f2f
Create Date: 2026-08-17 11:38:48.990342

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '494a0609b31d'
down_revision: Union[str, None] = '223993938f2f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('trades_account_id_fkey', 'trades', type_='foreignkey')
    op.create_foreign_key(
        'trades_account_id_fkey', 'trades', 'accounts', ['account_id'], ['id'], ondelete='RESTRICT'
    )


def downgrade() -> None:
    op.drop_constraint('trades_account_id_fkey', 'trades', type_='foreignkey')
    op.create_foreign_key(
        'trades_account_id_fkey', 'trades', 'accounts', ['account_id'], ['id'], ondelete='CASCADE'
    )
