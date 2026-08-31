from datetime import datetime

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import EVENT_GRACE_PERIOD, Event
from app.timeutils import to_utc, utc_now

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def index(
    request: Request,
    sport: str | None = None,
    db: Session = Depends(get_db),
):
    """Render the homepage with upcoming events, optionally filtered by sport."""
    # Upcoming events, plus ones that started within the grace period so a ride
    # in progress doesn't vanish from the list. Both sides are UTC, so this is
    # correct regardless of what timezone the server happens to run in.
    cutoff = utc_now() - EVENT_GRACE_PERIOD
    query = db.query(Event).filter(Event.date >= cutoff).order_by(Event.date)
    if sport:
        query = query.filter(Event.sport == sport)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "events": query.all(), "selected_sport": sport},
    )


@router.get("/events/new")
async def new_event_form(request: Request):
    """Render the empty form for creating a new event."""
    return templates.TemplateResponse("new_event.html", {"request": request})


@router.post("/events/new")
async def create_event(
    db: Session = Depends(get_db),
    sport: str = Form(...),
    title: str = Form(...),
    date: str = Form(...),
    meeting_point: str = Form(...),
    pace: str = Form(...),
    max_participants: str | None = Form(None),
    route_link: str | None = Form(None),
    description: str | None = Form(None),
    lat: str | None = Form(None),
    lng: str | None = Form(None),
):
    """Save a new event from submitted form data, then redirect to its detail page."""
    event = Event(
        sport=sport,
        title=title,
        # The Jinja form posts a bare wall clock with no offset, so this is
        # read as Munich local time and converted before storing.
        date=to_utc(datetime.fromisoformat(date)),
        meeting_point=meeting_point,
        pace=pace,
        max_participants=int(max_participants) if max_participants else None,
        route_link=route_link or None,
        description=description or None,
        lat=float(lat) if lat else None,
        lng=float(lng) if lng else None,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return RedirectResponse(url=f"/events/{event.id}", status_code=303)


@router.get("/events/{event_id}")
async def event_detail(event_id: int, request: Request, db: Session = Depends(get_db)):
    """Render the detail page for a single event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return templates.TemplateResponse(
        "event.html",
        {"request": request, "event": event},
    )
