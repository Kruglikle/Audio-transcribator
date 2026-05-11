from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from audio_transcribator.api.routes import router
from audio_transcribator.config import settings
from audio_transcribator.db import init_database
from audio_transcribator.ui.routes import router as ui_router


settings.ensure_dirs()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    yield


app = FastAPI(title="Audio/Video Processing API", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(settings.base_dir / "audio_transcribator" / "static")), name="static")
app.include_router(router)
app.include_router(ui_router)
