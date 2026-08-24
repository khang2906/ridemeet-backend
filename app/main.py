import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routes import events, rsvps
from app.routes import api


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Alembic owns schema creation — nothing to do at startup.
    yield


app = FastAPI(lifespan=lifespan)

# Allow the Next.js frontend to call this API from the browser.
# FRONTEND_ORIGIN should be set to the real deployed frontend URL in production;
# defaults to the local dev server so nothing needs configuring locally.
frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(events.router)
app.include_router(rsvps.router)
app.include_router(api.router)
