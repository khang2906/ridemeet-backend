"""Fill the database with realistic Munich test events.

Run from the backend directory:

    python -m scripts.seed

Safe to run repeatedly: events are matched by title, and existing ones are
skipped rather than duplicated. Nothing is ever deleted.

Dates are computed relative to *now* rather than hardcoded, so the seed data
never goes stale. (Hardcoded dates are how the original test events ended up
in the past, invisible behind the upcoming-events filter.)
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Allow `python scripts/seed.py` as well as `python -m scripts.seed`: without
# this, the plain-path form puts scripts/ on sys.path instead of the project
# root, and `import app...` fails.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal  # noqa: E402
from app.models import RSVP, Event  # noqa: E402


def at(days: int, hour: int, minute: int = 0) -> datetime:
    """A datetime `days` from now, at the given wall-clock time."""
    target = datetime.now() + timedelta(days=days)
    return target.replace(hour=hour, minute=minute, second=0, microsecond=0)


# (event fields, list of RSVP names)
SEED_EVENTS: list[tuple[dict, list[str]]] = [
    (
        {
            "sport": "bike",
            "title": "Feierabendrunde Isar",
            "date": at(1, 18, 30),
            "meeting_point": "Flaucher, Munich",
            "lat": 48.1112,
            "lng": 11.5514,
            "pace": "relaxed, 22–25 km/h",
            "max_participants": 12,
            "description": "Easy spin along the Isar. Flat, no one gets dropped.",
            "route_link": "https://www.komoot.com/tour/123456789",
        },
        ["Anna", "Jonas", "Mira"],
    ),
    (
        {
            "sport": "bike",
            "title": "Starnberger See Rundfahrt",
            "date": at(3, 9, 0),
            "meeting_point": "Starnberg Bahnhof",
            "lat": 47.9967,
            "lng": 11.3406,
            "pace": "moderate, 26–29 km/h",
            "max_participants": 8,
            "description": "Full loop around the lake, coffee stop in Tutzing. ~75 km.",
            "route_link": "https://www.strava.com/routes/987654321",
        },
        ["Sebastian", "Katrin"],
    ),
    (
        {
            # Deliberately full: exercises the "x / y going" display at capacity.
            "sport": "bike",
            "title": "Samstags-Gruppenausfahrt",
            "date": at(5, 8, 0),
            "meeting_point": "Olympiapark, Munich",
            "lat": 48.1755,
            "lng": 11.5518,
            "pace": "fast, 30+ km/h",
            "max_participants": 4,
            "description": "Quick group ride north. Bring a spare tube.",
            "route_link": None,
        },
        ["Lukas", "Ferdinand", "Nele", "Tobias"],
    ),
    (
        {
            "sport": "run",
            "title": "Englischer Garten Morgenlauf",
            "date": at(2, 7, 0),
            "meeting_point": "Monopteros, Englischer Garten",
            "lat": 48.1626,
            "lng": 11.5906,
            "pace": "5:30 min/km",
            "max_participants": 15,
            "description": "10 km before work. Conversational pace.",
            "route_link": None,
        },
        ["Pia"],
    ),
    (
        {
            # No RSVPs: exercises the "be the first" empty state.
            "sport": "run",
            "title": "Westpark Intervalle",
            "date": at(4, 18, 0),
            "meeting_point": "Westpark, Munich",
            "lat": 48.1224,
            "lng": 11.5253,
            "pace": "4:45 min/km",
            "max_participants": None,
            "description": "8 × 400 m with jog recovery. Warm up beforehand.",
            "route_link": None,
        },
        [],
    ),
    (
        {
            "sport": "motorcycle",
            "title": "Tegernsee Kurvenfahrt",
            "date": at(6, 10, 0),
            "meeting_point": "Tegernsee",
            "lat": 47.7100,
            "lng": 11.7583,
            "pace": "relaxed touring",
            "max_participants": 6,
            "description": "Alpine roads south, lunch at the lake. Rain cancels.",
            "route_link": "https://www.komoot.com/tour/222333444",
        },
        ["Marco", "Ines"],
    ),
]


def main() -> None:
    """Insert any seed events that aren't in the database yet."""
    db = SessionLocal()
    try:
        created = 0
        for fields, rsvp_names in SEED_EVENTS:
            existing = db.query(Event).filter(Event.title == fields["title"]).first()
            if existing is not None:
                print(f"  skip   {fields['title']} (already exists)")
                continue

            event = Event(**fields)
            # Appending to the relationship lets SQLAlchemy set event_id itself,
            # so there's no need to flush first to get the new event's id.
            event.rsvps = [RSVP(name=name) for name in rsvp_names]
            db.add(event)
            created += 1
            print(f"  create {fields['title']} ({len(rsvp_names)} RSVPs)")

        db.commit()
        print(f"\n{created} event(s) created, {len(SEED_EVENTS) - created} skipped.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
