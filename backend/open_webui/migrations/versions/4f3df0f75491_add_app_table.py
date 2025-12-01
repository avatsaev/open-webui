"""Add app table

Revision ID: 4f3df0f75491
Revises: 37f288994c47
Create Date: 2025-12-01 17:48:11.782664

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from open_webui.internal.db import JSONField
from open_webui.migrations.util import get_existing_tables


# revision identifiers, used by Alembic.
revision: str = '4f3df0f75491'
down_revision: Union[str, None] = '37f288994c47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    existing_tables = set(get_existing_tables())
    
    if "app" not in existing_tables:
        op.create_table(
            "app",
            sa.Column("id", sa.Text(), nullable=False),
            sa.Column("user_id", sa.Text(), nullable=False),
            sa.Column("source_chat_id", sa.Text(), nullable=True),
            sa.Column("title", sa.Text(), nullable=False),
            sa.Column("source_code", sa.Text(), nullable=False),
            sa.Column("params", JSONField(), nullable=True),
            sa.Column("meta", JSONField(), nullable=True),
            sa.Column("access_control", sa.JSON(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=True),
            sa.Column("updated_at", sa.BigInteger(), nullable=True),
            sa.Column("created_at", sa.BigInteger(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade() -> None:
    op.drop_table("app")
