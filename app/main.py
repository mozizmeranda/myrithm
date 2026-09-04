import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.database import init_db
from app.errors import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler
)

from app.routers import auth, user, streams, activity, leads, motivation
from app.routers.admin import (
    auth as admin_auth,
    streams as admin_streams,
    exercises as admin_exercises,
    tracks as admin_tracks,
    leads as admin_leads,
    stats as admin_stats
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure DB tables exist on application startup
init_db()

app = FastAPI(
    title="«Мой ритм» Backend API",
    description="Backend веб-сервиса коротких интервальных тренировок «Мой ритм»",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Exception handlers for unified error format
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Mount local media storage
settings.MEDIA_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.MEDIA_DIR), name="media")

# Register routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(streams.router)
app.include_router(activity.router)
app.include_router(leads.router)
app.include_router(motivation.router)

# Admin routers
app.include_router(admin_auth.router)
app.include_router(admin_streams.router)
app.include_router(admin_exercises.router)
app.include_router(admin_tracks.router)
app.include_router(admin_leads.router)
app.include_router(admin_stats.router)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "app": "MyRhythm"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8083)
