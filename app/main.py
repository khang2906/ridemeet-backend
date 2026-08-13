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

# Allow the Next.js dev server to call this API from the browser.
# In production this should be replaced with the real deployed frontend URL.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(events.router)
app.include_router(rsvps.router)
app.include_router(api.router)
