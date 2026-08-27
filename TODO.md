# Göle — TODO

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
- [ ] Mobile layout check on a real iPhone — fixing as issues turn up (most
      recent: `h-screen` → `h-dvh` on the homepage, since iOS Safari's
      address bar made `100vh` taller than the visible viewport)
- [ ] Deploy to Fly.io or Railway

## v1 refinements to consider

- [ ] Pace field: switch from label (relaxed/moderate/fast) to km/h range (e.g. 25–30 km/h)
- [ ] Enforce max_participants on RSVP, plus a waitlist that auto-promotes when someone cancels

## v2 and beyond

- [ ] GPX file upload and display (explicitly out of scope for v1)
- [ ] User accounts and authentication
