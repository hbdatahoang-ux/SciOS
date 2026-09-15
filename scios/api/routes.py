from fastapi import APIRouter, Depends, HTTPException

from scios.api.controller import SciOSController
from scios.api.schemas import (
    CSVAnalyzeRequest,
    CSVAnalyzeResponse,
    ReasonRequest,
    ReasonResponse,
    RunRequest,
    RunResponse,
    StatusResponse,
)
from scios.api.dependencies import get_scios
from scios.application.csv_analysis import CSVAnalysisApplication
from scios.cognitive_core.planner import Goal

router = APIRouter()


def _csv_failure_response(exc: RuntimeError) -> HTTPException:
    cause = exc.__cause__

    if isinstance(cause, FileNotFoundError):
        return HTTPException(
            status_code=404,
            detail="CSV file not found.",
        )

    from pandas.errors import EmptyDataError, ParserError

    if isinstance(cause, EmptyDataError):
        return HTTPException(
            status_code=400,
            detail="CSV file is empty.",
        )

    if isinstance(cause, ParserError):
        return HTTPException(
            status_code=400,
            detail="CSV file is malformed.",
        )

    return HTTPException(
        status_code=500,
        detail="CSV analysis failed.",
    )


@router.post("/run", response_model=RunResponse)
def run(request: RunRequest, scios=Depends(get_scios)):
    controller = SciOSController(scios)
    return controller.run(request)


@router.post("/reason", response_model=ReasonResponse)
def reason(request: ReasonRequest, scios=Depends(get_scios)):
    controller = SciOSController(scios)
    return controller.reason(request)


@router.post("/csv/analyze", response_model=CSVAnalyzeResponse)
def csv_analyze(request: CSVAnalyzeRequest):
    application = CSVAnalysisApplication(
        file_path=request.file_path,
    )

    goal = Goal(
        "Analyze the CSV dataset and explain anomalous values."
    )

    try:
        return application.analyze(
            goal=goal,
            query=request.query,
        )
    except RuntimeError as exc:
        raise _csv_failure_response(exc) from exc


@router.get("/status", response_model=StatusResponse)
def status(scios=Depends(get_scios)):
    controller = SciOSController(scios)
    return controller.status()


@router.get("/health")
def health(scios=Depends(get_scios)):
    controller = SciOSController(scios)
    return controller.health()
