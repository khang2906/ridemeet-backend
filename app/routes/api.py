from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import EVENT_GRACE_PERIOD, Event, RSVP
from app.timeutils import to_utc, utc_now
from app.schemas import EventCreate, EventListItem, EventResponse, RsvpCreate, RsvpResponse

router = APIRouter(prefix="/api")


@router.get("/events", response_model=list[EventListItem])
async def list_events(
    sport: str | None = None,
    db: Session = Depends(get_db),
) -> list[Event]:
    """Return upcoming events, optionally filtered by sport."""
    # Upcoming events, plus ones that started within the grace period so a ride
    # in progress doesn't vanish from the list. Both sides are UTC, so this is
    # correct regardless of what timezone the server happens to run in.
    cutoff = utc_now() - EVENT_GRACE_PERIOD
    query = db.query(Event).filter(Event.date >= cutoff).order_by(Event.date)
    if sport:
        query = query.filter(Event.sport == sport)
    return query.all()


@router.get("/events/{event_id}", response_model=EventResponse)
async def get_event(event_id: int, db: Session = Depends(get_db)) -> Event:
    """Return a single event with its RSVPs."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/events", response_model=EventResponse, status_code=201)
async def create_event(body: EventCreate, db: Session = Depends(get_db)) -> Event:
    """Create a new event from a JSON body."""
    fields = body.model_dump()
    # The client should send an offset-carrying ISO string; if it doesn't, the
    # value is read as Munich local time rather than silently treated as UTC.
    fields["date"] = to_utc(fields["date"])
    event = Event(**fields)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.post("/events/{event_id}/rsvp", response_model=RsvpResponse, status_code=201)
async def create_rsvp(
    event_id: int,
    body: RsvpCreate,
    db: Session = Depends(get_db),
) -> RSVP:
    """Add an RSVP to an event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    rsvp = RSVP(event_id=event_id, name=body.name)
    db.add(rsvp)
    db.commit()
    db.refresh(rsvp)
    return rsvp
