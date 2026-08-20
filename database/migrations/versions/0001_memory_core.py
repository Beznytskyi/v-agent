"""Create V-Agent memory core tables.

Revision ID: 0001_memory_core
Revises:
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_memory_core"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        "entities",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("type", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("metadata", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_entities_type", "entities", ["type"])
    op.create_index("ix_entities_name", "entities", ["name"])

    op.create_table(
        "facts",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("entity_id", uuid, sa.ForeignKey("entities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("attribute", sa.String(128), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("source_id", uuid),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("valid_from", sa.DateTime(timezone=True)),
        sa.Column("valid_until", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(32), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_facts_entity_id", "facts", ["entity_id"])
    op.create_index("ix_facts_attribute", "facts", ["attribute"])
    op.create_index("ix_facts_status", "facts", ["status"])

    op.create_table(
        "events",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("event_type", sa.String(128), nullable=False),
        sa.Column("entity_id", uuid, sa.ForeignKey("entities.id", ondelete="SET NULL")),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_id", uuid),
        sa.Column("metadata", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
    )
    op.create_index("ix_events_event_type", "events", ["event_type"])
    op.create_index("ix_events_entity_id", "events", ["entity_id"])
    op.create_index("ix_events_occurred_at", "events", ["occurred_at"])

    op.create_table(
        "decisions",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("decision", sa.Text(), nullable=False),
        sa.Column("reason", sa.Text()),
        sa.Column("alternatives", postgresql.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("decision_maker", sa.String(255)),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="active"),
        sa.Column("outcome", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_decisions_decided_at", "decisions", ["decided_at"])
    op.create_index("ix_decisions_status", "decisions", ["status"])

    op.create_table(
        "agent_runs",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("agent_name", sa.String(128), nullable=False),
        sa.Column("objective", sa.Text(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="queued"),
        sa.Column("input", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("context", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("result", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("error", sa.Text()),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_agent_runs_agent_name", "agent_runs", ["agent_name"])
    op.create_index("ix_agent_runs_status", "agent_runs", ["status"])


def downgrade() -> None:
    op.drop_table("agent_runs")
    op.drop_table("decisions")
    op.drop_table("events")
    op.drop_table("facts")
    op.drop_table("entities")
