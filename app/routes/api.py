from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Event, RSVP
from app.schemas import EventCreate, EventListItem, EventResponse, RsvpCreate, RsvpResponse

router = APIRouter(prefix="/api")


@router.get("/events", response_model=list[EventListItem])
async def list_events(
    sport: str | None = None,
    db: Session = Depends(get_db),
) -> list[Event]:
    """Return upcoming events, optionally filtered by sport."""
    query = db.query(Event).order_by(Event.date)
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
    event = Event(**body.model_dump())
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
