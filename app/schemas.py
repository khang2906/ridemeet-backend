from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RsvpResponse(BaseModel):
    id: int
    event_id: int
    name: str
    created_at: datetime

    # from_attributes lets Pydantic read fields off a SQLAlchemy object instead
    # of requiring a plain dict. Without this, returning an ORM instance errors.
    model_config = ConfigDict(from_attributes=True)


class EventResponse(BaseModel):
    id: int
    sport: str
    title: str
    date: datetime
    meeting_point: str
    route_link: str | None
    description: str | None
    pace: str
    max_participants: int | None
    lat: float | None
    lng: float | None
    rsvps: list[RsvpResponse]

    model_config = ConfigDict(from_attributes=True)


class EventListItem(BaseModel):
    """Lighter shape for the list endpoint — omits rsvps to avoid N+1 bloat."""
    id: int
    sport: str
    title: str
    date: datetime
    meeting_point: str
    pace: str
    max_participants: int | None
    lat: float | None
    lng: float | None

    model_config = ConfigDict(from_attributes=True)


class EventCreate(BaseModel):
    sport: str
    title: str
    date: datetime
    meeting_point: str
    pace: str
    max_participants: int | None = None
    route_link: str | None = None
    description: str | None = None
    lat: float | None = None
    lng: float | None = None


class RsvpCreate(BaseModel):
    name: str
