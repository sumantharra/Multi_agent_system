"""create invoices and invoice_items tables

Revision ID: 20260908_0004
Revises: 20260908_0003
Create Date: 2026-09-08 23:24:00

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260908_0004"
down_revision: str | Sequence[str] | None = "20260908_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "invoices",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("hostel_id", sa.Uuid(), nullable=False),
        sa.Column("invoice_number", sa.String(length=80), nullable=False),
        sa.Column("billing_month", sa.String(length=7), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("total_quantity", sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column("subtotal", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("tax", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("adjustments", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("total_amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column(
            "payment_status",
            sa.String(length=20),
            server_default="unpaid",
            nullable=False,
        ),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("source_document_id", sa.Uuid(), nullable=True),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "hostel_id",
            "billing_month",
            name="uq_invoices_hostel_billing_month",
        ),
        sa.UniqueConstraint("invoice_number", name="uq_invoices_invoice_number"),
    )
    op.create_index(op.f("ix_invoices_hostel_id"), "invoices", ["hostel_id"])
    op.create_index(
        "ix_invoices_payment_status_due_date",
        "invoices",
        ["payment_status", "due_date"],
    )
    op.create_index(
        "ix_invoices_hostel_id_billing_month",
        "invoices",
        ["hostel_id", "billing_month"],
    )

    op.create_table(
        "invoice_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("invoice_id", sa.Uuid(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column("rate", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoices.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_invoice_items_invoice_id"), "invoice_items", ["invoice_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_invoice_items_invoice_id"), table_name="invoice_items")
    op.drop_table("invoice_items")
    op.drop_index("ix_invoices_hostel_id_billing_month", table_name="invoices")
    op.drop_index("ix_invoices_payment_status_due_date", table_name="invoices")
    op.drop_index(op.f("ix_invoices_hostel_id"), table_name="invoices")
    op.drop_table("invoices")
