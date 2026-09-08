"""create deliveries table

Revision ID: 20260908_0003
Revises: 20260812_0002
Create Date: 2026-09-08 17:23:00

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260908_0003"
down_revision: str | Sequence[str] | None = "20260812_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "deliveries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("hostel_id", sa.Uuid(), nullable=False),
        sa.Column("delivery_date", sa.Date(), nullable=False),
        sa.Column("morning_quantity", sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column("evening_quantity", sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column("total_quantity", sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column("rate_per_liter", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["hostel_id"], ["hostels.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("hostel_id", "delivery_date", name="uq_deliveries_hostel_date"),
    )
    op.create_index(
        "ix_deliveries_hostel_id_delivery_date",
        "deliveries",
        ["hostel_id", "delivery_date"],
    )
    op.create_index(op.f("ix_deliveries_hostel_id"), "deliveries", ["hostel_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_deliveries_hostel_id"), table_name="deliveries")
    op.drop_index("ix_deliveries_hostel_id_delivery_date", table_name="deliveries")
    op.drop_table("deliveries")
