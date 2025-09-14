import os, uuid, datetime
from fastapi import UploadFile, HTTPException

ALLOWED = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


def save_local_image(base_dir: str, user_id: str, file: UploadFile) -> str:
    ext = ALLOWED.get(file.content_type)
    if not ext:
        raise HTTPException(status_code=415, detail="Unsupported image type")
    today = datetime.datetime.now().strftime("%Y/%m/%d")
    folder = os.path.join(base_dir, user_id, today)
    os.makedirs(folder, exist_ok=True)
    fname = f"{uuid.uuid4()}{ext}"
    path = os.path.join(folder, fname)
    with open(path, "wb") as f:
        f.write(file.file.read())
    return path
