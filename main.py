"""Main application entry point for Cortex API.

This module sets up the FastAPI application with all necessary configurations,
middleware, and routes for the Engineering Thinking Training Platform.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_crons import Crons, get_cron_router
from contextlib import asynccontextmanager
import time
from database import connect_to_mongo, close_mongo_connection
from routers import auth, users, tasks, responses, progress, drills, admin
from config import settings
from logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle: startup and shutdown events.
    
    This context manager handles:
    - Startup: Establish MongoDB connection
    - Shutdown: Close MongoDB connection gracefully
    
    Args:
        app: The FastAPI application instance
    """
    logger.info("Starting Cortex API server...")
    # Startup: Connect to MongoDB database
    await connect_to_mongo()
    logger.info("Database connection established")
    logger.info("Cron jobs initialized (daily task generation at midnight)")
    
    yield
    
    # Shutdown: Clean up database connections
    logger.info("Shutting down Cortex API server...")
    await close_mongo_connection()
    logger.info("Database connection closed")


app = FastAPI(
    title="Cortex API",
    description="Engineering Thinking Training Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Initialize cron jobs
crons = Crons(app)

# Add cron management endpoints
app.include_router(get_cron_router(), prefix="/api/crons", tags=["Cron Jobs"])


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and their processing time."""
    start_time = time.time()
    
    # Log request
    logger.info(f"-> {request.method} {request.url.path} | Client: {request.client.host}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = (time.time() - start_time) * 1000
    
    # Log response
    logger.info(
        f"<- {request.method} {request.url.path} | "
        f"Status: {response.status_code} | "
        f"Time: {process_time:.2f}ms"
    )
    
    return response


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(responses.router, prefix="/api/responses", tags=["Responses"])
app.include_router(progress.router, prefix="/api/progress", tags=["Progress"])
app.include_router(drills.router, prefix="/api/drills", tags=["Thinking Drills"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])


# Register cron jobs with decorator
from cron_jobs import daily_task_generation_job

@crons.cron("0 0 * * *", name="daily_task_generation")
async def scheduled_task_generation():
    """Runs at midnight every day to generate tasks for all roles."""
    return await daily_task_generation_job()


@app.get("/")
async def root():
    """Root endpoint to verify API is running.
    
    Returns:
        dict: API status information including name, version, and status
    """
    return {
        "message": "Cortex API - Engineering Thinking Training Platform",
        "version": "1.0.0",
        "status": "active"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
