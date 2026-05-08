from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from audio_transcribator.api.routes import router
from audio_transcribator.config import settings
from audio_transcribator.ui.routes import router as ui_router


settings.ensure_dirs()

app = FastAPI(title="Audio/Video Processing API")
app.mount("/static", StaticFiles(directory=str(settings.base_dir / "audio_transcribator" / "static")), name="static")
app.include_router(router)
app.include_router(ui_router)
