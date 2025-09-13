from typing import Any, Optional, Dict


def api_response(
    success: bool, message: str = "", payload: Any = None, meta: Optional[Dict] = None
):
    # unified API shape: { success, message, payload, meta }
    return {"success": success, "message": message, "payload": payload, "meta": meta}
