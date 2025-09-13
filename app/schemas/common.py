from typing import Optional
from pydantic import BaseModel


class Meta(BaseModel):
    page: Optional[int] = None
    size: Optional[int] = None
    total: Optional[int] = None
