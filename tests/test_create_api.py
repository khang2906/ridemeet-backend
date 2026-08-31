"""The write endpoints: creating events and RSVPs.

These matter more than they look. POST /api/events is where an incoming date
actually passes through to_utc(), and where the "every event needs a real map
pin" rule is enforced — neither is visible from the read endpoints.
"""

from datetime import timedelta

from app.models import Event
from app.timeutils import utc_now


def valid_event(**overrides) -> dict:
    """A complete, valid create-event body; override one field per test."""
    body = {
        "sport": "bike",
        "title": "Feierabendrunde",
        "date": (utc_now() + timedelta(days=1)).isoformat(),
        "meeting_point": "Flaucher",
        "pace": "25 km/h",
        "lat": 48.1112,
        "lng": 11.5514,
    }
    body.update(overrides)
    return body


def test_creating_an_event_returns_it_with_an_id(client):
    response = client.post("/api/events", json=valid_event())

    assert response.status_code == 201
    assert response.json()["id"] > 0
    assert response.json()["title"] == "Feierabendrunde"


def test_a_created_event_appears_in_the_list(client):
    client.post("/api/events", json=valid_event(title="Brand new"))

    assert "Brand new" in [e["title"] for e in client.get("/api/events").json()]


def test_a_date_with_an_offset_is_stored_as_utc(client, db_session):
    # 18:30 in Munich (+02:00) is 16:30 UTC. Storing the wall clock unchanged
    # would put the ride two hours late for everyone.
    client.post("/api/events", json=valid_event(date="2027-09-01T18:30:00+02:00"))

    stored = db_session.query(Event).one()
    assert (stored.date.hour, stored.date.minute) == (16, 30)


def test_a_naive_date_is_read_as_munich_local_time(client, db_session):
    # The Jinja form and older clients send no offset. Treating that as UTC
    # would silently shift the event; it's read as local time instead.
    client.post("/api/events", json=valid_event(date="2027-09-01T18:30:00"))

    stored = db_session.query(Event).one()
    assert (stored.date.hour, stored.date.minute) == (16, 30)


def test_coordinates_are_required(client):
    body = valid_event()
    del body["lat"]

    # 422 is FastAPI rejecting the body against EventCreate, before any handler
    # code runs — the schema is the enforcement point, not the route.
    assert client.post("/api/events", json=body).status_code == 422


def test_optional_fields_default_to_null(client):
    created = client.post("/api/events", json=valid_event()).json()

    assert created["route_link"] is None
    assert created["description"] is None
    assert created["max_participants"] is None


def test_rsvp_is_added_to_the_event(client):
    event_id = client.post("/api/events", json=valid_event()).json()["id"]

    response = client.post(f"/api/events/{event_id}/rsvp", json={"name": "Anna"})
    assert response.status_code == 201

    detail = client.get(f"/api/events/{event_id}").json()
    assert [r["name"] for r in detail["rsvps"]] == ["Anna"]


def test_multiple_rsvps_are_kept_in_order(client):
    event_id = client.post("/api/events", json=valid_event()).json()["id"]

    for name in ["Anna", "Jonas", "Mira"]:
        client.post(f"/api/events/{event_id}/rsvp", json={"name": name})

    detail = client.get(f"/api/events/{event_id}").json()
    assert [r["name"] for r in detail["rsvps"]] == ["Anna", "Jonas", "Mira"]


def test_rsvp_to_a_missing_event_returns_404(client):
    assert client.post("/api/events/9999/rsvp", json={"name": "Anna"}).status_code == 404


def test_max_participants_is_not_enforced_yet(client):
    """Documents current behaviour: capacity is displayed, not enforced.

    Deliberate for v1 — enforcement plus a waitlist is in TODO.md. This test
    exists so that when someone implements it, a red test tells them the
    contract changed rather than the change slipping by unnoticed.
    """
    event_id = client.post("/api/events", json=valid_event(max_participants=1)).json()["id"]

    client.post(f"/api/events/{event_id}/rsvp", json={"name": "Anna"})
    second = client.post(f"/api/events/{event_id}/rsvp", json={"name": "Jonas"})

    assert second.status_code == 201
