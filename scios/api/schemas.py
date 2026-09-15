from typing import Any, Dict

from pydantic import BaseModel


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


class CSVAnalyzeRequest(BaseModel):
    file_path: str
    query: str


class CSVAnalyzeResponse(BaseModel):
    goal: str
    rows: int
    columns: int
    column_names: list[str]
    missing: dict[str, int]
    outliers: dict[str, Any]
    reasoning: list[dict[str, Any]]
