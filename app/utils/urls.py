from pathlib import Path
from fastapi import Request
from app.core.config import settings


def public_upload_url(request: Request, stored_path: str) -> str:
    """
    Convert a stored path (either absolute path inside UPLOAD_DIR, or a string that
    already starts with 'uploads/') into a public URL at /uploads/<rel>.
    """
    # Normalize base
    uploads_root = Path(settings.UPLOAD_DIR).resolve()

    p = Path(stored_path)
    # Try to compute relative path under uploads/
    rel: str | None = None
    try:
        rel = p.resolve().relative_to(uploads_root).as_posix()
    except Exception:
        s = str(stored_path).replace("\\", "/")
        # handle old rows that stored "./uploads/..."
        if "/uploads/" in s:
            rel = s.split("/uploads/", 1)[1]
        elif s.startswith("uploads/"):
            rel = s.split("uploads/", 1)[1]
        else:
            # final fallback: just the filename (may break if not under uploads)
            rel = p.name

    # starlette StaticFiles mount name is "uploads"
    return str(request.url_for("uploads", path=rel))
