from fastapi import FastAPI, Request, Response, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config.settings import settings
from app.config.database import engine, Base
from app.controllers import project_controller, review_controller, user_controller, experience_controller, skill_controller, contact_controller, project_category_controller, chatbot_controller
from app.jobs.scheduler import init_scheduler, shutdown_scheduler
from app.dependencies.database import get_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Define lifespan context for FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables and initialize scheduler
    logger.info("Application starting up...")
    Base.metadata.create_all(bind=engine)
    scheduler = init_scheduler()
    
    yield
    
    # Shutdown: Gracefully stop the scheduler
    logger.info("Application shutting down...")
    shutdown_scheduler()

# Create FastAPI app
app = FastAPI(
    title="Portfolio Website API",
    description="A FastAPI MVC application for managing portfolio content",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"},
    )

# Include routers
app.include_router(
    user_controller.router,
    prefix=settings.API_PREFIX
)

app.include_router(
    project_controller.router,
    prefix=settings.API_PREFIX
)

app.include_router(
    review_controller.router,
    prefix=settings.API_PREFIX
)

app.include_router(
    experience_controller.router,
    prefix=settings.API_PREFIX
)

app.include_router(
    skill_controller.router,
    prefix=settings.API_PREFIX
)

app.include_router(
    project_category_controller.router,
    prefix=settings.API_PREFIX
)
app.include_router(
    contact_controller.router,
    prefix=settings.API_PREFIX
)

app.include_router(
    chatbot_controller.router,
    prefix=settings.API_PREFIX
)

@app.get("/")
def root():
    return {"message": "Welcome to the Portfolio Website API"}

@app.get("/healthz", status_code=status.HTTP_200_OK)
async def health_check(
    request: Request, 
    response: Response,
    db: Session = Depends(get_db)
):
    # Check if request has payload
    if await request.body():
        response.status_code = status.HTTP_400_BAD_REQUEST
        return
    
    # Set no-cache header
    response.headers["Cache-Control"] = "no-cache"
    
    # Check database connection
    try:
        # Execute a simple query to test connection
        db.execute(text("SELECT 1"))
        
        # Return 200 OK with no content
        response.status_code = status.HTTP_200_OK
        return None
    except SQLAlchemyError as e:
        logger.error(f"Database connection error: {e}")
        # Return 503 Service Unavailable with no content
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
