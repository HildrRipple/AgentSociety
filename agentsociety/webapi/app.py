import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .api import api_router
from .models._base import Base

__all__ = ["create_app"]

_script_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_script_dir)

def create_app(
    pg_dsn: str,
    mqtt_broker: str,
    mqtt_username: str,
    mqtt_password: str,
    mlflow_url: str,
    read_only: bool,
):

    # https://fastapi.tiangolo.com/advanced/events/#use-case
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Init database when app starts
        engine = create_async_engine(pg_dsn)
        session_factory = async_sessionmaker(engine)
        # save session_factory to app state
        app.state.get_db = session_factory

        # save read_only to app state
        app.state.read_only = read_only
        # save mlflow_url to app state
        app.state.mlflow_url = mlflow_url

        # TODO: Init MQTT client
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield

    # 创建FastAPI应用
    app = FastAPI(
        title="AgentSociety WebUI API",
        lifespan=lifespan,
    )

    # https://stackoverflow.com/questions/75958222/can-i-return-400-error-instead-of-422-error
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": exc.errors()},
        )

    app.include_router(api_router)

    # serve frontend files
    frontend_path = Path(_parent_dir) / "_dist"
    app.mount("/", StaticFiles(directory=frontend_path, html=True))

    # 404 handler, redirect all 404 to index.html except /api
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: HTTPException):
        if not request.url.path.startswith("/api"):
            return FileResponse(frontend_path / "index.html")
        return exc

    return app
