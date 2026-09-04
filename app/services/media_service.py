import os
import uuid
from pathlib import Path
from fastapi import UploadFile
from app.config import settings
from app.errors import AppException

ALLOWED_VIDEO_MIME_TYPES = {"video/mp4", "video/webm", "video/x-matroska", "application/octet-stream"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".webm", ".mkv"}

ALLOWED_AUDIO_MIME_TYPES = {"audio/mpeg", "audio/mp3", "audio/wav", "audio/x-wav", "application/octet-stream"}
ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav"}

MAX_FILE_SIZE = 150 * 1024 * 1024  # 150 MB

class MediaService:
    @staticmethod
    async def save_media_file(file: UploadFile, is_video: bool = True) -> str:
        filename = file.filename or "file"
        ext = Path(filename).suffix.lower()

        allowed_exts = ALLOWED_VIDEO_EXTENSIONS if is_video else ALLOWED_AUDIO_EXTENSIONS
        if ext not in allowed_exts:
            raise AppException("INVALID_FILE_TYPE", f"Invalid file extension. Allowed: {', '.join(allowed_exts)}", 400)

        # Check content type if available
        if file.content_type:
            allowed_mimes = ALLOWED_VIDEO_MIME_TYPES if is_video else ALLOWED_AUDIO_MIME_TYPES
            if file.content_type.lower() not in allowed_mimes and ext not in allowed_exts:
                raise AppException("INVALID_FILE_TYPE", f"Invalid file MIME type: {file.content_type}", 400)

        target_dir = settings.VIDEOS_DIR if is_video else settings.AUDIO_DIR
        target_dir.mkdir(parents=True, exist_ok=True)

        unique_name = f"{uuid.uuid4().hex[:12]}{ext}"
        target_path = target_dir / unique_name

        file_size = 0
        try:
            with open(target_path, "wb") as out_file:
                while chunk := await file.read(1024 * 1024):
                    file_size += len(chunk)
                    if file_size > MAX_FILE_SIZE:
                        target_path.unlink(missing_ok=True)
                        raise AppException("FILE_TOO_LARGE", f"File size exceeds limit of {MAX_FILE_SIZE // (1024 * 1024)}MB", 400)
                    out_file.write(chunk)
        except Exception:
            target_path.unlink(missing_ok=True)
            raise

        sub_folder = "videos" if is_video else "audio"
        return f"/media/{sub_folder}/{unique_name}"

    @staticmethod
    def delete_local_file_if_unused(url_path: str, count_references_fn):
        if not url_path or not url_path.startswith("/media/"):
            return
        
        # Check if another record uses the same file
        if count_references_fn(url_path) > 0:
            return

        rel_path = url_path.lstrip("/")
        full_path = Path(".") / rel_path
        if full_path.exists() and full_path.is_file():
            try:
                full_path.unlink(missing_ok=True)
            except Exception:
                pass
