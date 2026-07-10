from pydantic import BaseModel
from typing import Any, Dict

class RunRequest(BaseModel):
    task: str

class RunResponse(BaseModel):
    result: Dict[str, Any]

class ReasonRequest(BaseModel):
    context: Dict[str, Any]

class ReasonResponse(BaseModel):
    conclusions: list[str]

class StatusResponse(BaseModel):
    status: str
    uptime: float
