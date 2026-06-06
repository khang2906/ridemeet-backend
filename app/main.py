from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Event, RSVP


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Alembic owns schema creation — nothing to do at startup.
    yield


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def index(
    request: Request,
    sport: str | None = None,
    db: Session = Depends(get_db),
):
    """Render the homepage with upcoming events, optionally filtered by sport."""
    # Query parameters (e.g. ?sport=bike) become function arguments automatically.
    # Build the query in pieces so we can conditionally add a WHERE clause.
    query = db.query(Event).order_by(Event.date)
    if sport:
        query = query.filter(Event.sport == sport)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "events": query.all(), "selected_sport": sport},
    )


@app.get("/events/new")
async def new_event_form(request: Request):
    """Render the empty form for creating a new event."""
    return templates.TemplateResponse("new_event.html", {"request": request})


@app.post("/events/new")
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
        date=datetime.fromisoformat(date),  # datetime-local sends "2026-05-20T08:00"
        meeting_point=meeting_point,
        pace=pace,
        # HTML forms submit empty fields as "" (never null), so coerce blanks to None
        max_participants=int(max_participants) if max_participants else None,
        route_link=route_link or None,
        description=description or None,
        lat=float(lat) if lat else None,
        lng=float(lng) if lng else None,
    )
    db.add(event)
    db.commit()
    db.refresh(event)  # reloads the row so event.id (assigned by the DB) is available
    return RedirectResponse(url=f"/events/{event.id}", status_code=303)


@app.get("/events/{event_id}")
async def event_detail(event_id: int, request: Request, db: Session = Depends(get_db)):
    """Render the detail page for a single event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return templates.TemplateResponse(
        "event.html",
        {"request": request, "event": event},
    )


@app.post("/events/{event_id}/rsvp")
async def create_rsvp(
    event_id: int,
    db: Session = Depends(get_db),
    name: str = Form(...),
):
    """Add an RSVP to an event, then redirect back to its detail page."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    db.add(RSVP(event_id=event_id, name=name))
    db.commit()
    return RedirectResponse(url=f"/events/{event_id}", status_code=303)
