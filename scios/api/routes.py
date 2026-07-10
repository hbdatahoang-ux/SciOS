from fastapi import APIRouter, Depends
from scios.api.controller import SciOSController
from scios.api.schemas import RunRequest, RunResponse, ReasonRequest, ReasonResponse, StatusResponse
from scios.api.dependencies import get_scios

router = APIRouter()

@router.post("/run", response_model=RunResponse)
def run(request: RunRequest, scios=Depends(get_scios)):
    controller = SciOSController(scios)
    return controller.run(request)

@router.post("/reason", response_model=ReasonResponse)
def reason(request: ReasonRequest, scios=Depends(get_scios)):
    controller = SciOSController(scios)
    return controller.reason(request)

@router.get("/status", response_model=StatusResponse)
def status(scios=Depends(get_scios)):
    controller = SciOSController(scios)
    return controller.status()

@router.get("/health")
def health(scios=Depends(get_scios)):
    controller = SciOSController(scios)
    return controller.health()
