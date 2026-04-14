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
            content={
                "status": "error",
                "message": exc.message,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": "Validation failed",
                "details": exc.errors(),
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "message": exc.detail,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        # For unexpected exceptions
        return JSONResponse(
            status_code=500,
            content={
                "status": "Error",
                "message": "Internal server error",
            },
        )


async def conditional_validation_handler(request: Request, exc: RequestValidationError):
    # Inspect all errors raised by Pydantic
    errors = exc.errors()

    # Check if the "value" field was missing
    missing_value_error = any(
        err.get("loc")[-1] == "value" and err.get("type") == "missing"
        for err in errors
    )

    if missing_value_error:
        # Override only this case to 400
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": 'Missing or empty name parameter.',
                "details": errors,
            },
        )

    # For all other validation errors, keep default FastAPI behavior (422)
    from fastapi.exception_handlers import request_validation_exception_handler
    return await request_validation_exception_handler(request, exc)