from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Event, RSVP

router = APIRouter()


@router.post("/events/{event_id}/rsvp")
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
