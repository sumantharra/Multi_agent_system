"""create documents table

Revision ID: 20260909_0007
Revises: 20260909_0006
Create Date: 2026-09-09 17:10:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

revision: str = "20260909_0007"
down_revision: str | Sequence[str] | None = "20260909_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("hostel_id", sa.Uuid(), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("storage_key", sa.String(length=500), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("document_type", sa.String(length=40), nullable=False),
        sa.Column(
            "processing_status",
            sa.String(length=30),
            nullable=False,
            server_default="queued",
        ),
        sa.Column(
            "extraction_status",
            sa.String(length=30),
            nullable=False,
            server_default="not_started",
        ),
        sa.Column("extracted_payload", JSONB(), nullable=True),
        sa.Column("extraction_issues", JSONB(), nullable=True),
        sa.Column("content_hash", sa.String(length=64), nullable=True),
        sa.Column("uploaded_by", sa.Uuid(), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("confirmed_by", sa.Uuid(), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_by", sa.Uuid(), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["hostel_id"], ["hostels.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["confirmed_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["rejected_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_documents_hostel_id"), "documents", ["hostel_id"])
    op.create_index(
        "ix_documents_processing_status_created_at",
        "documents",
        ["processing_status", "created_at"],
    )
    op.create_index(
        "uq_documents_content_hash_hostel_id",
        "documents",
        ["content_hash", "hostel_id"],
        unique=True,
        postgresql_where=sa.text("content_hash IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_documents_content_hash_hostel_id", table_name="documents")
    op.drop_index("ix_documents_processing_status_created_at", table_name="documents")
    op.drop_index(op.f("ix_documents_hostel_id"), table_name="documents")
    op.drop_table("documents")
