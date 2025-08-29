# app/handlers.py

import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from .exceptions import AIAnalysisError, ReportError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def ai_analysis_exception_handler(request: Request, exc: AIAnalysisError):
    """Handles exceptions raised from the AI service."""
    logger.error(f"AIAnalysisError on path {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=500,
        content={
            "ok": False,
            "error": {
                "code": "ai_analysis_failed",
                "message": exc.message
            }
        },
    )

async def report_exception_handler(request: Request, exc: ReportError):
    """Handles exceptions raised during report operations."""
    logger.error(f"ReportError on path {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=500,
        content={
            "ok": False,
            "error": {
                "code": "report_operation_failed",
                "message": exc.message
            }
        },
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """Handles any other unexpected exceptions."""
    logger.critical(f"An unhandled exception occurred on path {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "ok": False,
            "error": {
                "code": "internal_server_error",
                "message": "An unexpected internal error occurred. The issue has been logged."
            }
        },
    )
