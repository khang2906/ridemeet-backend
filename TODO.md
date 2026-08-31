# RideMeet — TODO

## v1 remaining

- [x] Database: SQLAlchemy models + SQLite setup
- [x] Event detail page
- [x] Event creation form
- [x] Map showing meeting point (Leaflet + OpenStreetMap)
- [x] RSVP form (name only, no account)
- [x] RSVP list on event detail page
- [x] Filter event list by sport (city filter deferred — location will become structured via picker)
- [x] Set up DB migrations (Alembic)
- [x] Rebuild frontend in Next.js + React + Tailwind + shadcn/ui — Komoot-style:
      full-height map, floating collapsible list panel (desktop) / draggable
      bottom sheet (mobile), floating detail panel with RSVP on selection
- [x] Mobile layout check on a real iPhone — create, map pin, pace, and RSVP
      all exercised from the phone. Fixes along the way: `h-screen` → `h-dvh`
      on the homepage (iOS Safari's address bar made `100vh` taller than the
      visible viewport), and the draggable bottom sheet below `md:`.
- [x] Filter out past events (3h grace period so a ride in progress stays
      visible — see `EVENT_GRACE_PERIOD` in `models.py`)
- [x] Seed script for realistic test data (`python -m scripts.seed`)

## Before deploying

- [ ] **Timezone.** Stored dates are the *browser's* wall clock; `datetime.now()`
      in the list routes is the *server's*. Both naive, so they agree locally and
      disagree once hosted: a UTC server sits 2h behind Munich in summer (1h in
      winter), so events linger ~2h past when they should drop off the list.
      Nothing looks broken, which is what makes it easy to miss.
      Fix for v1: set `TZ=Europe/Berlin` on the host — one config line, no code.
      Proper fix if RideMeet ever spans regions: store timezone-aware UTC and
      render in the viewer's zone (migration + both frontends + a backfill).
- [ ] Move the SQLite path off a bare relative string in `database.py` — or
      skip it, since `DATABASE_URL` replaces it at the Postgres switch.
- [ ] SQLite → Postgres (Neon project already created, EU region)
- [ ] Deploy to Fly.io or Railway

## v1 refinements to consider

- [ ] Pace field: switch from label (relaxed/moderate/fast) to km/h range (e.g. 25–30 km/h)
- [ ] Enforce max_participants on RSVP, plus a waitlist that auto-promotes when someone cancels

## v2 and beyond

- [ ] GPX file upload and display (explicitly out of scope for v1)
- [ ] User accounts and authentication
