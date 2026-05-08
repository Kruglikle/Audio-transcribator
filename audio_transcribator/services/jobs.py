import shutil
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from audio_transcribator.config import settings
from audio_transcribator.utils.files import tail


def build_job_result(job_id: str) -> dict:
    job_dir = settings.results_dir / job_id
    summary_file = job_dir / "summary.txt"
    transcript_file = job_dir / "transcript.txt"
    log_file = job_dir / "run.log"

    if not job_dir.exists():
        raise FileNotFoundError("Job not found")

    result = {"job_id": job_id, "files": [p.name for p in job_dir.iterdir() if p.is_file()]}

    if transcript_file.exists():
        result["transcript"] = transcript_file.read_text(encoding="utf-8", errors="replace")

    if summary_file.exists():
        result["summary"] = summary_file.read_text(encoding="utf-8", errors="replace")

    if log_file.exists():
        result["log_tail"] = tail(log_file)

    return result


def get_job_file(job_id: str, filename: str) -> Path:
    job_dir = settings.results_dir / job_id
    file_path = job_dir / filename

    if not job_dir.exists():
        raise FileNotFoundError("Job not found")

    if not file_path.exists():
        raise FileNotFoundError("File not found")

    return file_path


def start_uploaded_file(file: UploadFile) -> dict:
    job_id = str(uuid4())
    job_dir = settings.results_dir / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    safe_filename = file.filename or "upload"
    input_path = settings.upload_dir / f"{job_id}_{safe_filename}"

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    log_path = job_dir / "run.log"
    command = [sys.executable, "process_audio_fast.py", str(input_path), str(job_dir)]

    with open(log_path, "w", encoding="utf-8") as log_file:
        subprocess.Popen(
            command,
            cwd=str(settings.base_dir),
            stdout=log_file,
            stderr=log_file,
        )

    return {
        "status": "started",
        "job_id": job_id,
        "message": "File uploaded and processing started",
    }

