"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("reverted", sa.Boolean(), nullable=False, default=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "devices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("individual_address", sa.String(), nullable=True),
        sa.Column("template_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "parameters",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("param_id", sa.String(), nullable=False),
        sa.Column("value", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "com_objects",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.Column("co_id", sa.String(), nullable=False),
        sa.Column("dpt_major", sa.Integer(), nullable=False),
        sa.Column("dpt_minor", sa.Integer(), nullable=False),
        sa.Column("flag_communication", sa.Boolean(), nullable=False, default=True),
        sa.Column("flag_read", sa.Boolean(), nullable=False, default=False),
        sa.Column("flag_write", sa.Boolean(), nullable=False, default=False),
        sa.Column("flag_transmit", sa.Boolean(), nullable=False, default=False),
        sa.Column("flag_update", sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "links",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("start_pin", sa.Integer(), nullable=False),
        sa.Column("end_pin", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "areas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("area_number", sa.Integer(), nullable=False, unique=True),
        sa.Column("name", sa.String(), nullable=False, default=""),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "lines",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("area_id", sa.Integer(), nullable=False),
        sa.Column("line_number", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False, default=""),
        sa.ForeignKeyConstraint(["area_id"], ["areas.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("area_id", "line_number"),
    )


def downgrade() -> None:
    op.drop_table("lines")
    op.drop_table("areas")
    op.drop_table("links")
    op.drop_table("com_objects")
    op.drop_table("parameters")
    op.drop_table("devices")
    op.drop_table("events")
