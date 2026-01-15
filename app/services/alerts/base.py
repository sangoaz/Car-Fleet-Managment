from typing import Literal, Optional
from pydantic import BaseModel


AlertStatus = Literal["ok", "warning", "alert"]


class Alert(BaseModel):
    type: str
    status: AlertStatus
    message: Optional[str] = None
