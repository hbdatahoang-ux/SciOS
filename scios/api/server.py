from fastapi import FastAPI
from scios.api.routes import router

def create_app() -> FastAPI:
    """
    Create FastAPI app and mount routes.
    """
    app = FastAPI(title="SciOS API", version="0.3")
    app.include_router(router)
    return app

app = create_app()
