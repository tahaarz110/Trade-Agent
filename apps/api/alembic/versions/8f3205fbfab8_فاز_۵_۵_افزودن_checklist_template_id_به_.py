"""فاز ۵.۵: افزودن checklist_template_id به معاملات

Revision ID: 8f3205fbfab8
Revises: 494a0609b31d
Create Date: 2026-08-20 01:12:13.385960

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f3205fbfab8'
down_revision: Union[str, None] = '494a0609b31d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('trades', sa.Column('checklist_template_id', sa.UUID(), nullable=True))
    op.create_foreign_key(
        'trades_checklist_template_id_fkey', 'trades', 'checklist_templates',
        ['checklist_template_id'], ['id'], ondelete='SET NULL'
    )


def downgrade() -> None:
    op.drop_constraint('trades_checklist_template_id_fkey', 'trades', type_='foreignkey')
    op.drop_column('trades', 'checklist_template_id')
