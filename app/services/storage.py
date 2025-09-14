import os, uuid, datetime
from fastapi import UploadFile, HTTPException
from pathlib import Path
from app.core.config import settings

ALLOWED = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


def _ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def _bytes_limit() -> int:
    return int(settings.MAX_UPLOAD_MB) * 1024 * 1024


def save_local_image(base_dir: str, user_id: str, file: UploadFile) -> tuple[str, str]:
    """
    Returns (fs_path, rel_path) where:
      - fs_path = absolute or relative filesystem path to the saved file
      - rel_path = path relative to the UPLOAD_DIR (posix), suitable for /uploads/<rel_path>
    """
    ext = ALLOWED.get(file.content_type)
    if not ext:
        raise HTTPException(status_code=415, detail="Unsupported image type")

    # folder structure: uploads/<userId>/YYYY/MM/DD/
    today = datetime.datetime.now().strftime("%Y/%m/%d")
    root = Path(base_dir)
    folder = root / user_id / today
    _ensure_dir(folder)

    fname = f"{uuid.uuid4()}{ext}"
    fs_path = folder / fname  # filesystem path
    rel_path = fs_path.relative_to(root)  # path under uploads/

    # enforce max size and write in chunks
    limit = _bytes_limit()
    written = 0
    file.file.seek(0)
    with open(fs_path, "wb") as dst:
        while True:
            chunk = file.file.read(1024 * 1024)  # 1MB
            if not chunk:
                break
            written += len(chunk)
            if written > limit:
                try:
                    dst.close()
                    fs_path.unlink(missing_ok=True)
                finally:
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large (>{settings.MAX_UPLOAD_MB} MB)",
                    )
            dst.write(chunk)
    file.file.seek(0)

    # Return str() so callers can serialize easily
    # fs_path may be relative (if base_dir is relative) — that's OK for internal use.
    return str(fs_path), rel_path.as_posix()
