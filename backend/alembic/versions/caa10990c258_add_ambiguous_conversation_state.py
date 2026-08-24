"""Add ambiguous conversation state

Revision ID: caa10990c258
Revises: 6cba89ce1a80
Create Date: 2026-08-24 13:57:29.403666

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'caa10990c258'
down_revision: Union[str, Sequence[str], None] = '6cba89ce1a80'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "conversations",
        sa.Column(
            "pending_query",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "conversations",
        sa.Column(
            "pending_candidates",
            sa.JSON(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column(
        "conversations",
        "pending_candidates",
    )

    op.drop_column(
        "conversations",
        "pending_query",
    )