__all__ = ["app"]

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.router import router
from .exceptions import AIAnalysisError, ReportError
from .handlers import (
    ai_analysis_exception_handler,
    report_exception_handler,
    generic_exception_handler,
)

# Create FastAPI app
app = FastAPI(
    title="IdeaVisor API",
    description="AI-Powered Startup Validation Platform",
    version="1.0.0"
)

# Register exception handlers
app.add_exception_handler(AIAnalysisError, ai_analysis_exception_handler)
app.add_exception_handler(ReportError, report_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(router, prefix="/api/v1")
