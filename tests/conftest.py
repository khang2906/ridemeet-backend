"""Shared test fixtures.

Every test gets a fresh, empty, in-memory database. Nothing here ever touches
`groupride.db` (or Postgres) — tests that could delete your real events would
be tests you'd avoid running.
"""

import os

# app.database requires DATABASE_URL to exist at import time (see its
# docstring for why: a missing var should fail loudly, not fall back
# silently). setdefault, not straight assignment, so a real value already in
# the environment — a CI runner mimicking production, say — isn't clobbered.
# The value itself is never used: db_session/client below replace the app's
# real engine entirely before any test runs.
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def db_session():
    """A session against a throwaway in-memory database."""
    engine = create_engine(
        "sqlite://",  # no filename = in memory
        connect_args={"check_same_thread": False},
        # An in-memory SQLite database lives inside its connection. The default
        # pool hands out new connections, each of which would see a *different*
        # empty database — StaticPool reuses the one, so the schema created here
        # is the schema the test and the app both see.
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    """A TestClient whose requests hit the throwaway database."""
    # get_db is a FastAPI dependency, so it can be swapped without the routes
    # knowing — this is what dependency injection buys you at test time.
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        # try/finally, so a failure constructing TestClient (a broken lifespan,
        # say) can't leave the override in place for every later test — that
        # would bury the real error under a cascade of unrelated failures.
        app.dependency_overrides.clear()
