"""FastAPI application entrypoint.

Phase 0 scope: app factory, CORS, logging, generic error handling, and the
/health endpoint. Domain routers (accounts, trades, symbols, ...) are added
in later phases and simply get `include_router`-ed here.
"""
import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.logging_config import configure_logging
from app.routers import health

configure_logging()
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Professional ICT Trading Journal — Offline Intelligence Engine API",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def on_startup() -> None:
        settings.ensure_storage_dirs()
        logger.info(
            "Starting %s (env=%s, low_resource_mode=%s, ai_narrator_enabled=%s)",
            settings.app_name,
            settings.app_env,
            settings.low_resource_mode,
            settings.ai_narrator_enabled,
        )

    # --- Global error handling ------------------------------------------------
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.warning("Validation error on %s %s: %s", request.method, request.url.path, exc)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": "validation_error", "detail": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "internal_server_error", "detail": str(exc)},
        )

    # --- Routers ---------------------------------------------------------------
    app.include_router(health.router)

    @app.get("/")
    def root() -> dict:
        return {"service": settings.app_name, "status": "running"}

    return app


app = create_app()
