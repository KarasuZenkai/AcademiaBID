"""add learning assignments and course prerequisites

Revision ID: 8ad2e6c4f102
Revises: 4c86525ba651
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8ad2e6c4f102"
down_revision: Union[str, Sequence[str], None] = "4c86525ba651"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "academy_assignments",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("academy_id", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["academy_id"], ["academies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "academy_id", name="uq_academy_assignment_user_academy"),
    )
    op.create_index("ix_academy_assignments_user_id", "academy_assignments", ["user_id"])
    op.create_index("ix_academy_assignments_academy_id", "academy_assignments", ["academy_id"])
    op.create_table(
        "learning_path_assignments",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("learning_path_id", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["learning_path_id"], ["learning_paths.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "learning_path_id", name="uq_path_assignment_user_path"),
    )
    op.create_index("ix_learning_path_assignments_user_id", "learning_path_assignments", ["user_id"])
    op.create_index("ix_learning_path_assignments_learning_path_id", "learning_path_assignments", ["learning_path_id"])
    op.create_table(
        "module_assignments",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("module_id", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["module_id"], ["modules.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "module_id", name="uq_module_assignment_user_module"),
    )
    op.create_index("ix_module_assignments_user_id", "module_assignments", ["user_id"])
    op.create_index("ix_module_assignments_module_id", "module_assignments", ["module_id"])
    op.create_table(
        "course_prerequisites",
        sa.Column("course_id", sa.Uuid(), nullable=False),
        sa.Column("prerequisite_course_id", sa.Uuid(), nullable=False),
        sa.CheckConstraint("course_id <> prerequisite_course_id", name="ck_course_prerequisite_not_self"),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["prerequisite_course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("course_id", "prerequisite_course_id"),
        sa.UniqueConstraint("course_id", "prerequisite_course_id", name="uq_course_prerequisite"),
    )


def downgrade() -> None:
    op.drop_table("course_prerequisites")
    op.drop_index("ix_module_assignments_module_id", table_name="module_assignments")
    op.drop_index("ix_module_assignments_user_id", table_name="module_assignments")
    op.drop_table("module_assignments")
    op.drop_index("ix_learning_path_assignments_learning_path_id", table_name="learning_path_assignments")
    op.drop_index("ix_learning_path_assignments_user_id", table_name="learning_path_assignments")
    op.drop_table("learning_path_assignments")
    op.drop_index("ix_academy_assignments_academy_id", table_name="academy_assignments")
    op.drop_index("ix_academy_assignments_user_id", table_name="academy_assignments")
    op.drop_table("academy_assignments")
