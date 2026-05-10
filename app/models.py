from pydantic import BaseModel
from typing import Optional


class ReviewComment(BaseModel):
    path: str
    line: int
    severity: str   # bug | style | performance | security
    message: str
    suggestion: Optional[str] = None
