# RideMeet

A web app for organizing group meetups for cyclists, motorcyclists, and
runners. Post an event with a sport, date, meeting point, route, and pace —
others RSVP and join the ride.

## Status

v1 in progress. See [TODO.md](TODO.md).

## Tech stack

- **Language:** Python 3.11+ · FastAPI · SQLAlchemy 2.x · Alembic · SQLite
- **Maps:** Leaflet + OpenStreetMap, geocoding via Nominatim
- **Two frontends:**
  - **v1** — server-rendered Jinja2 templates + HTMX, served by this app at `/`
  - **v2** — a separate Next.js app ([ridemeet-frontend](https://github.com/khang2906/ridemeet-frontend))
    that talks to the JSON routes under `/api/`. The v1 templates stay until v2 is deployed.

## Running locally

```
python -m venv .venv
.venv\Scripts\activate           # Windows PowerShell
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0
```

Open http://localhost:8000 for the v1 HTML UI, or http://localhost:8000/docs for
FastAPI's generated API docs.

Two things that look optional but aren't:

- **`app.main:app`**, not `main:app` — the module path is a dotted Python import,
  and `main.py` lives inside the `app/` package.
- **`--host 0.0.0.0`** — without it uvicorn binds loopback only, which blocks the
  Next.js frontend once it's pointed at this machine's LAN IP for phone testing.

## Migrations

```
alembic upgrade head            # apply
alembic revision --autogenerate -m "describe the change"
```
