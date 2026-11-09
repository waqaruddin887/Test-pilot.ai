"""Transactional run delivery; existing queued runs are backfilled once."""

import time
import uuid

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    table = op.create_table(
        "outbox_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "job_id",
            sa.String(36),
            sa.ForeignKey("jobs.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("generation", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(20), nullable=False),
        sa.Column("failures", sa.Integer(), nullable=False),
        sa.Column("next_attempt_at", sa.Float(), nullable=False),
        sa.Column("published_at", sa.Float(), nullable=True),
        sa.CheckConstraint("state IN ('pending','published','suppressed','expired')"),
        sa.CheckConstraint("generation >= 0 AND failures >= 0"),
    )
    op.create_index("ix_outbox_events_state", "outbox_events", ["state"])
    connection = op.get_bind()
    jobs = connection.execute(
        sa.text(
            "SELECT jobs.id FROM jobs JOIN runs ON runs.id=jobs.run_id WHERE runs.state='queued' AND jobs.state='pending'"
        )
    )
    for (job_id,) in jobs:
        connection.execute(
            table.insert().values(
                id=str(uuid.uuid4()),
                job_id=job_id,
                generation=0,
                state="pending",
                failures=0,
                next_attempt_at=time.time(),
            )
        )


def downgrade():
    op.drop_index("ix_outbox_events_state", table_name="outbox_events")
    op.drop_table("outbox_events")
