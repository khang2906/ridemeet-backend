from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, field_validator


class UtcDatetimeMixin:
    """Guarantees outgoing datetimes carry an explicit UTC offset.

    Stored values come back naive from SQLite (it has no timezone-aware type),
    and a naive ISO string is parsed by JavaScript as *local* time — so an event
    at 16:30 UTC would render as 16:30 Munich instead of 18:30. Tagging them
    here makes the API contract unambiguous no matter what the database returns.
    """

    @field_validator("date", "created_at", mode="after", check_fields=False)
    @classmethod
    def _assume_utc(cls, value: datetime) -> datetime:
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


class RsvpResponse(UtcDatetimeMixin, BaseModel):
    id: int
    event_id: int
    name: str
    created_at: datetime

    # from_attributes lets Pydantic read fields off a SQLAlchemy object instead
    # of requiring a plain dict. Without this, returning an ORM instance errors.
    model_config = ConfigDict(from_attributes=True)


class EventResponse(UtcDatetimeMixin, BaseModel):
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


class EventListItem(UtcDatetimeMixin, BaseModel):
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
    # Required (unlike on Event/EventResponse) so every new event gets a real map
    # pin — enforced here at creation time rather than with a DB migration, since
    # the column itself stays nullable for old rows created before this rule existed.
    lat: float
    lng: float
    max_participants: int | None = None
    route_link: str | None = None
    description: str | None = None


class RsvpCreate(BaseModel):
    name: str
