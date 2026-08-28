"""Add last resolved OSB state to conversations.

Revision ID: 4f9a6c2d8b17
Revises: 93deccb20018
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4f9a6c2d8b17"
down_revision: Union[str, Sequence[str], None] = "93deccb20018"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("conversations", sa.Column("last_osb_id", sa.Integer(), nullable=True))
    op.add_column("conversations", sa.Column("last_osb_name", sa.String(length=255), nullable=True))
    op.add_column("conversations", sa.Column("last_intent", sa.String(length=100), nullable=True))
    op.add_column("conversations", sa.Column("last_requested_field", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("conversations", "last_requested_field")
    op.drop_column("conversations", "last_intent")
    op.drop_column("conversations", "last_osb_name")
    op.drop_column("conversations", "last_osb_id")
