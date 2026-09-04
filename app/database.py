import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Reads .env into the process environment if one exists (local dev). On a real
# host the platform sets DATABASE_URL directly, so there's nothing to load —
# this is a no-op there, not an error.
load_dotenv()


def get_database_url() -> str:
    """The database to connect to, read from the environment.

    Required rather than defaulting to a local SQLite file: a missing
    DATABASE_URL should fail loudly and immediately, not silently fall back to
    an empty local database that happens to satisfy every query with zero rows.
    Also used by alembic/env.py, so the app and its migrations can never point
    at two different databases.
    """
    url = os.environ["DATABASE_URL"]

    # Neon (and most managed Postgres providers) hand out a bare
    # "postgresql://" URL. SQLAlchemy needs the driver named explicitly, or it
    # falls back to psycopg2, which isn't installed here — psycopg (v3) is.
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)

    return url


# check_same_thread=False was SQLite-only — FastAPI's thread pool otherwise
# gets rejected by SQLite's single-creator-thread rule. Postgres has no such
# restriction, so the connect_args that were here are gone, not just unused.
engine = create_engine(get_database_url())

SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Yield a database session and guarantee it closes after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
