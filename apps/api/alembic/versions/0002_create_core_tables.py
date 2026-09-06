"""Create core tables: businesses, ownership_classifications, sources, community_submissions.

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-06
"""

from collections.abc import Sequence

import geoalchemy2
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_CLASSIFICATION_VALUES = (
    "'family_owned','locally_owned','independent','franchise','corporate_owned','unknown'"
)


def upgrade() -> None:
    op.create_table(
        "businesses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("address", postgresql.JSONB(), nullable=True),
        sa.Column(
            "location",
            geoalchemy2.Geography(geometry_type="POINT", srid=4326, spatial_index=False),
            nullable=False,
        ),
        sa.Column("categories", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("contact", postgresql.JSONB(), nullable=True),
        sa.Column("brand", sa.String(), nullable=True),
        sa.Column("parent_company", sa.String(), nullable=True),
        sa.Column("provider", sa.String(), nullable=True),
        sa.Column("provider_place_id", sa.String(), nullable=True),
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
        sa.UniqueConstraint("provider", "provider_place_id", name="uq_business_provider_identity"),
    )
    op.create_index("ix_businesses_location", "businesses", ["location"], postgresql_using="gist")

    op.create_table(
        "ownership_classifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "business_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("classification", sa.String(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "confidence >= 0.0 AND confidence <= 1.0",
            name="ck_classification_confidence_range",
        ),
        sa.CheckConstraint(
            f"classification IN ({_CLASSIFICATION_VALUES})",
            name="ck_classification_value",
        ),
    )
    op.create_index(
        "ix_ownership_classifications_business_id",
        "ownership_classifications",
        ["business_id"],
    )

    op.create_table(
        "sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "business_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "classification_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ownership_classifications.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("url", sa.String(), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("snippet", sa.Text(), nullable=True),
    )
    op.create_index("ix_sources_business_id", "sources", ["business_id"])
    op.create_index("ix_sources_classification_id", "sources", ["classification_id"])

    op.create_table(
        "community_submissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "business_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("proposed_classification", sa.String(), nullable=False),
        sa.Column("evidence", sa.Text(), nullable=True),
        sa.Column("submitter_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            f"proposed_classification IN ({_CLASSIFICATION_VALUES})",
            name="ck_submission_classification_value",
        ),
        sa.CheckConstraint(
            "status IN ('pending','approved','rejected')",
            name="ck_submission_status_value",
        ),
    )
    op.create_index(
        "ix_community_submissions_business_id",
        "community_submissions",
        ["business_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_community_submissions_business_id", table_name="community_submissions")
    op.drop_table("community_submissions")
    op.drop_index("ix_sources_classification_id", table_name="sources")
    op.drop_index("ix_sources_business_id", table_name="sources")
    op.drop_table("sources")
    op.drop_index(
        "ix_ownership_classifications_business_id",
        table_name="ownership_classifications",
    )
    op.drop_table("ownership_classifications")
    op.drop_index("ix_businesses_location", table_name="businesses")
    op.drop_table("businesses")
