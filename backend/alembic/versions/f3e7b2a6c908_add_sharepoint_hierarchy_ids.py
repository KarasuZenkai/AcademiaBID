"""store SharePoint folder identities for catalog hierarchy

Revision ID: f3e7b2a6c908
Revises: 8ad2e6c4f102
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f3e7b2a6c908"
down_revision: Union[str, Sequence[str], None] = "8ad2e6c4f102"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _add_folder_identity(table: str) -> None:
    op.add_column(table, sa.Column("sharepoint_drive_id", sa.String(length=512), nullable=True))
    op.add_column(table, sa.Column("sharepoint_item_id", sa.String(length=512), nullable=True))
    op.create_index(f"ix_{table}_sharepoint_drive_id", table, ["sharepoint_drive_id"])
    op.create_index(f"ix_{table}_sharepoint_item_id", table, ["sharepoint_item_id"])


def upgrade() -> None:
    for table in ("academies", "learning_paths", "courses", "modules"):
        _add_folder_identity(table)


def _drop_folder_identity(table: str) -> None:
    op.drop_index(f"ix_{table}_sharepoint_item_id", table_name=table)
    op.drop_index(f"ix_{table}_sharepoint_drive_id", table_name=table)
    op.drop_column(table, "sharepoint_item_id")
    op.drop_column(table, "sharepoint_drive_id")


def downgrade() -> None:
    for table in ("modules", "courses", "learning_paths", "academies"):
        _drop_folder_identity(table)
