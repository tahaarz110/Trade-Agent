"""فاز ۵.۵: افزودن is_active به آیتم‌های چک‌لیست

Revision ID: 7ad35794c2a0
Revises: 8f3205fbfab8
Create Date: 2026-08-20 01:15:56.532377

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ad35794c2a0'
down_revision: Union[str, None] = '8f3205fbfab8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # server_default موقت برای پرکردن ردیف‌های موجود بدون از دست دادن
    # داده؛ سپس default در سطح سرور حذف می‌شود تا مدل (که default را در
    # سطح اپلیکیشن/Python مدیریت می‌کند) تنها منبع صدق بماند.
    op.add_column(
        'checklist_items',
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.alter_column('checklist_items', 'is_active', server_default=None)


def downgrade() -> None:
    op.drop_column('checklist_items', 'is_active')
