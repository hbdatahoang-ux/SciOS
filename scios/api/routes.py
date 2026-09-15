from fastapi import APIRouter, Depends

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

    return application.analyze(
        goal=goal,
        query=request.query,
    )


@router.get("/status", response_model=StatusResponse)
def status(scios=Depends(get_scios)):
    controller = SciOSController(scios)
    return controller.status()


@router.get("/health")
def health(scios=Depends(get_scios)):
    controller = SciOSController(scios)
    return controller.health()
