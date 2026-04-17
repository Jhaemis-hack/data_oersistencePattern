from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from .exceptions import AppException


def register_error_handlers(app: FastAPI):

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"status": "error", "message": exc.message},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"status": "error", "message": exc.detail},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Internal server error"},
        )


async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    for err in errors:
        if err.get("type") == "missing" and "name" in err.get("loc", []):
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Missing or empty name"},
            )
    return JSONResponse(
        status_code=422,
        content={"status": "error", "message": "Invalid type"},
    )
