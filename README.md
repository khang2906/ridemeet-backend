# RideMeet

A web app for organizing group meetups for cyclists, motorcyclists, and
runners. Post an event with a sport, date, meeting point, route, and pace —
others RSVP and join the ride.

## Status

v1 in progress. See [TODO.md](TODO.md).

## Tech stack

- **Backend:** Python 3.11+ · FastAPI · SQLAlchemy 2.x · SQLite
- **Frontend:** Server-rendered Jinja2 templates
- **Maps (planned):** Leaflet + OpenStreetMap

## Running locally

```
python -m venv .venv
.venv\Scripts\activate          # Windows PowerShell
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://localhost:8000.
