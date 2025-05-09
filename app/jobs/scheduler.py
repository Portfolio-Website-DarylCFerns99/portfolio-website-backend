from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone, timedelta
import logging
from app.models.project_model import Project
from app.utils.github_utils import fetch_github_data
from app.config.database import SessionLocal
import uuid

logger = logging.getLogger(__name__)

# Create scheduler instance
scheduler = AsyncIOScheduler()

async def refresh_expired_projects():
    """
    Cron job to check for expired GitHub projects and refresh their data.
    Runs once per day at 3:00 AM.
    """
    logger.info("Starting scheduled job to refresh expired GitHub projects")
    
    # Get current time with timezone awareness
    now = datetime.now(timezone.utc)
    
    # Create DB session
    db = SessionLocal()
    try:
        # Query for expired GitHub projects
        query = (
            select(Project)
            .where(
                (Project.type == "github") & 
                (Project.expiry_date < now) &
                (Project.url.is_not(None))
            )
        )
        
        expired_projects = db.execute(query).scalars().all()
        logger.info(f"Found {len(expired_projects)} expired GitHub projects to refresh")
        
        # Refresh each expired project
        for project in expired_projects:
            try:
                logger.info(f"Refreshing project ID: {project.id}, URL: {project.url}")
                
                # Fetch new GitHub data
                _, github_full_data = await fetch_github_data(project.url)
                
                # Update the project with timezone-aware datetime
                # Set expiry to tomorrow at 3 AM UTC
                tomorrow = now.replace(hour=3, minute=0, second=0, microsecond=0)
                tomorrow = tomorrow.replace(day=tomorrow.day + 1)
                
                project.additional_data = github_full_data
                project.expiry_date = tomorrow
                
                logger.info(f"Successfully refreshed project ID: {project.id}")
            except Exception as e:
                logger.error(f"Error refreshing project ID {project.id}: {str(e)}")
                # Continue with next project
        
        # Commit all changes
        db.commit()
        logger.info("Completed refreshing expired GitHub projects")
        
    except Exception as e:
        logger.error(f"Error in refresh_expired_projects job: {str(e)}")
        db.rollback()
    finally:
        db.close()

def init_scheduler():
    """Initialize the scheduler with jobs"""
    
    # Add job to refresh expired projects - runs daily at 3:00 AM
    scheduler.add_job(
        refresh_expired_projects,
        CronTrigger(hour=3, minute=0),
        id="refresh_expired_projects",
        name="Refresh expired GitHub projects",
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start()
    logger.info("Scheduler started with configured jobs")
    
    return scheduler

def shutdown_scheduler():
    """Shutdown the scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler shutdown")
