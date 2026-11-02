import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from sqlalchemy.exc import SQLAlchemyError


logger = logging.getLogger("air_quality")

class InvalidCSVError(Exception):
    pass

def register_exception_handlers(app: FastAPI):

    @app.exception_handler(InvalidCSVError)
    async def invalid_csv_handler(
        request: Request,
        exc: InvalidCSVError
    ):

        logger.warning(f"Invalid CSV file: {exc}")

        return JSONResponse(
            status_code=400,
            content={
                "error": str(exc)
            }
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):

        logger.warning(f"HTTP error: {exc.detail}")

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
    ):

        logger.warning(f"Validation error: {exc.errors()}")

        return JSONResponse(
            status_code=422,
            content={
                "error": "Invalid request data",
                "details": exc.errors()
            }
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_exception_handler(
        request: Request,
        exc: SQLAlchemyError
    ):

        logger.exception("Database error")

        return JSONResponse(
            status_code=500,
            content={
                "error": "Database operation failed"
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):

        logger.exception("Unexpected server error")

        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error"
            }
        )