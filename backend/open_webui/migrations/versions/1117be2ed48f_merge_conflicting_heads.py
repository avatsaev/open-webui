"""merge_conflicting_heads

Revision ID: 1117be2ed48f
Revises: 3e0e00844bb0, 4f3df0f75491
Create Date: 2025-12-03 15:29:05.438631

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import open_webui.internal.db


# revision identifiers, used by Alembic.
revision: str = '1117be2ed48f'
down_revision: Union[str, None] = ('3e0e00844bb0', '4f3df0f75491')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
