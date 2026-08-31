"""The /api/events list endpoint.

Mostly about the grace period: the list promises "upcoming" events but
deliberately keeps showing a ride for a few hours after it starts, because
that's when someone running late still needs the meeting point.
"""

from datetime import timedelta

from app.models import EVENT_GRACE_PERIOD, Event
from app.timeutils import utc_now


def make_event(db, *, hours_from_now: float, sport: str = "bike", title: str = "Ride"):
    """Insert one event at a time relative to now, and return it."""
    event = Event(
        sport=sport,
        title=title,
        date=utc_now() + timedelta(hours=hours_from_now),
        meeting_point="Flaucher",
        pace="25 km/h",
        lat=48.1112,
        lng=11.5514,
    )
    db.add(event)
    db.commit()
    return event


def titles(response):
    return [event["title"] for event in response.json()]


def test_future_event_is_listed(client, db_session):
    make_event(db_session, hours_from_now=3, title="Later today")
    assert titles(client.get("/api/events")) == ["Later today"]


def test_event_inside_the_grace_period_is_still_listed(client, db_session):
    # Started an hour ago: the ride is happening right now.
    make_event(db_session, hours_from_now=-1, title="In progress")
    assert titles(client.get("/api/events")) == ["In progress"]


def test_event_past_the_grace_period_is_hidden(client, db_session):
    hours = EVENT_GRACE_PERIOD.total_seconds() / 3600
    make_event(db_session, hours_from_now=-(hours + 1), title="Long over")
    assert titles(client.get("/api/events")) == []


def test_events_are_returned_in_date_order(client, db_session):
    make_event(db_session, hours_from_now=48, title="Later")
    make_event(db_session, hours_from_now=24, title="Sooner")
    assert titles(client.get("/api/events")) == ["Sooner", "Later"]


def test_sport_filter_narrows_the_list(client, db_session):
    make_event(db_session, hours_from_now=24, sport="bike", title="Ride")
    make_event(db_session, hours_from_now=25, sport="run", title="Run")
    assert titles(client.get("/api/events?sport=run")) == ["Run"]


def test_dates_are_returned_with_an_explicit_utc_offset(client, db_session):
    # A naive ISO string would be parsed by the browser as *local* time, showing
    # an 18:30 ride as 16:30. The offset is part of the API contract.
    make_event(db_session, hours_from_now=24)
    date = client.get("/api/events").json()[0]["date"]
    assert date.endswith("Z") or "+00:00" in date


def test_detail_endpoint_still_returns_a_past_event(client, db_session):
    # Hidden from the list, but a direct link must keep working — someone
    # opening an old URL should see the ride, not a 404.
    event = make_event(db_session, hours_from_now=-72, title="Last week")
    response = client.get(f"/api/events/{event.id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Last week"


def test_missing_event_returns_404(client):
    assert client.get("/api/events/9999").status_code == 404
