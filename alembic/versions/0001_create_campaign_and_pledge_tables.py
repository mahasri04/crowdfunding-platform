"""create campaign and pledge tables

Revision ID: 0001
Revises:
Create Date: 2026-04-21 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "campaigns",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("goal", sa.Float(), nullable=False),
        sa.Column("pledged", sa.Float(), nullable=False, server_default="0"),
        sa.Column("deadline", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "pledges",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("user_name", sa.String(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
    )
    op.create_index("ix_campaigns_id", "campaigns", ["id"])
    op.create_index("ix_pledges_id", "pledges", ["id"])
    op.create_index("ix_pledges_campaign_id", "pledges", ["campaign_id"])


def downgrade() -> None:
    op.drop_index("ix_pledges_campaign_id", table_name="pledges")
    op.drop_index("ix_pledges_id", table_name="pledges")
    op.drop_index("ix_campaigns_id", table_name="campaigns")
    op.drop_table("pledges")
    op.drop_table("campaigns")
