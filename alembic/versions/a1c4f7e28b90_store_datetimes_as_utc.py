"""store datetimes as UTC

Two things happen here.

1. The columns become timezone-aware. On Postgres that's a real TIMESTAMPTZ; on
   SQLite it changes nothing, since SQLite has no timezone-aware type at all.
   The declaration is what matters — it carries the intent to Postgres later.

2. Existing rows are converted. Every stored datetime so far is a Munich
   wall-clock time (that's what the browser and the Jinja form submitted), so
   each one is reinterpreted as Europe/Berlin and rewritten as UTC. Doing this
   inside a migration rather than a script matters: Alembic runs it exactly
   once, and a second run of a standalone backfill would shift everything twice.

Revision ID: a1c4f7e28b90
Revises: 507b13dce0a6
Create Date: 2026-08-31
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import sqlalchemy as sa
from alembic import op

revision = "a1c4f7e28b90"
down_revision = "507b13dce0a6"
branch_labels = None
depends_on = None

LOCAL_TZ = ZoneInfo("Europe/Berlin")

# (table, column) pairs holding datetimes that need converting.
DATETIME_COLUMNS = [("events", "date"), ("rsvps", "created_at")]


def _shift(to_utc: bool) -> None:
    """Rewrite every stored datetime between Munich local time and UTC.

    ZoneInfo rather than a fixed offset, so summer rows shift by 2 hours and
    winter rows by 1 — a single hardcoded offset would corrupt half the data.
    """
    connection = op.get_bind()

    for table, column in DATETIME_COLUMNS:
        rows = connection.execute(
            sa.text(f"SELECT id, {column} FROM {table} WHERE {column} IS NOT NULL")
        ).fetchall()

        for row_id, value in rows:
            # SQLite hands back strings; Postgres hands back datetimes.
            if isinstance(value, str):
                value = datetime.fromisoformat(value)

            if to_utc:
                converted = value.replace(tzinfo=LOCAL_TZ).astimezone(timezone.utc)
            else:
                converted = value.replace(tzinfo=timezone.utc).astimezone(LOCAL_TZ)

            # Stored without the offset: SQLite drops tzinfo anyway, and keeping
            # the written shape identical to what SQLAlchemy writes avoids two
            # different formats living in the same column.
            connection.execute(
                sa.text(f"UPDATE {table} SET {column} = :value WHERE id = :id"),
                {"value": converted.replace(tzinfo=None), "id": row_id},
            )


def upgrade() -> None:
    for table, column in DATETIME_COLUMNS:
        with op.batch_alter_table(table) as batch_op:
            batch_op.alter_column(
                column, type_=sa.DateTime(timezone=True), existing_nullable=False
            )
    _shift(to_utc=True)


def downgrade() -> None:
    _shift(to_utc=False)
    for table, column in DATETIME_COLUMNS:
        with op.batch_alter_table(table) as batch_op:
            batch_op.alter_column(
                column, type_=sa.DateTime(), existing_nullable=False
            )
