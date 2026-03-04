"""add_task_table

Revision ID: a1b2c3d4e5f6
Revises: d774176c44a3
Create Date: 2026-03-03 16:30:00.000000

"""

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "d774176c44a3"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "task",
        sa.Column(
            "task_type", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False
        ),
        sa.Column("queue", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "rq_job_id", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True
        ),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("kwargs", sa.JSON(), nullable=True),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("error", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_task_rq_job_id"), "task", ["rq_job_id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_task_rq_job_id"), table_name="task")
    op.drop_table("task")
