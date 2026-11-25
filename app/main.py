from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.health import router as health_router
from app.api.users import router as users_router
from app.core.config import get_settings
from app.db.session import engine
from app.services.exceptions import (
    NotFoundError,
    ConflictError,
    ValidationError,
    ForbiddenError
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    await engine.dispose()


settings = get_settings()

app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)


@app.exception_handler(NotFoundError)
async def not_found_error(_:Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(ConflictError)
async def conflict_error(_:Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": exc.message})

@app.exception_handler(ValidationError)
async def validation_error(_:Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": exc.message})

@app.exception_handler(ForbiddenError)
async def forbidden_error(_:Request, exc: ForbiddenError) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": exc.message})





app.include_router(health_router)
app.include_router(users_router)
