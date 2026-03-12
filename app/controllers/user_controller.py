from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user_model import User
from app.models.skill_model import Skill, SkillGroup
from app.models.experience_model import Experience
from app.models.project_model import Project
from app.models.project_category_model import ProjectCategory
from app.models.review_model import Review
from app.models.portfolio_mv_model import PortfolioMV
from app.schemas.user_schema import UserResponse, UserUpdate
from app.security.password import verify_password
from app.security.token import create_access_token
from app.services.user_service import UserService
from datetime import datetime, timedelta
import logging
import json
import math
from dateutil.relativedelta import relativedelta
from uuid import UUID
from cachetools import TTLCache

logger = logging.getLogger(__name__)

# Cache for the heavy public portfolio data payload (memory cache)
portfolio_cache = TTLCache(maxsize=1000, ttl=86400) # 24hr cache

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return a JWT token.
    """
    # Find user by username
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # If user not found, try with email
    if not user:
        user = db.query(User).filter(User.email == form_data.username).first()
    
    # If still no user or password doesn't match
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate access token
    access_token_expires = timedelta(minutes=120)  # 2 hours
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    # Create user response
    user_response = UserResponse.model_validate(user)
    
    # Return token and user data
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }

@router.get("/profile", response_model=UserResponse)
def get_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get the current user's profile information.
    """
    return current_user

@router.put("/profile", response_model=UserResponse)
def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the current user's profile information.
    Accepts a UserUpdate object with any fields to update.
    For document-type social links, the url field should contain base64-encoded file data.
    Only the provided fields will be updated.
    If featured_skill_ids are provided, they will be validated against the skills table.
    Only skill IDs that exist in the database will be stored.
    """
    try:
        # Extract user data
        user_data = user_update.model_dump(exclude_unset=True)
                
        # Validate unique fields if they're being updated
        if "username" in user_data and user_data["username"] != current_user.username:
            existing_user = db.query(User).filter(User.username == user_data["username"]).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists"
                )
        
        if "email" in user_data and user_data["email"] != current_user.email:
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
        
        # Use the user service to update the profile with validation for featured skills
        user_service = UserService(db)
        updated_user = user_service.update_user_profile(current_user, user_update)
        
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data format: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating profile: {str(e)}"
        )

def calculate_total_experience(experiences):
    """
    Calculate the total years of experience from a list of experience objects.
    Rounds down to the floor value and adds a "+" if there's a fractional part.
    
    Args:
        experiences (list): List of experience objects with start_date and end_date
        
    Returns:
        str: Total years of experience as a floor value with "+" if there's a fraction
    """
    # Filter for objects with type "experience"
    experience_objects = [exp for exp in experiences if exp.type == "experience"]
    
    # Initialize total experience in years
    total_experience_years = 0
    
    for exp in experience_objects:
        # Get start and end dates
        start_date = datetime.strptime(exp.start_date.strftime("%Y-%m-%d"), "%Y-%m-%d")
        
        # Use end_date if available, otherwise use today's date
        if exp.end_date:
            end_date = datetime.strptime(exp.end_date.strftime("%Y-%m-%d"), "%Y-%m-%d")
        else:
            end_date = datetime.now()
        
        # Calculate the difference
        diff = relativedelta(end_date, start_date)
        
        # Convert to years (including partial years)
        years = diff.years + (diff.months / 12) + (diff.days / 365.25)
        
        # Add to total
        total_experience_years += years
    
    # Get the floor value
    floor_years = round(total_experience_years)

    if floor_years < 2:
        return floor_years
    
    # Check if there's any fractional part
    if total_experience_years > floor_years:
        # Return floor value with "+"
        return f"{floor_years}+"
    else:
        # Return just the floor value as string
        return str(floor_years)

@router.get("/public-data/{user_id}")
def get_public_data(user_id: UUID, db: Session = Depends(get_db)):
    """
    Get all public data for the portfolio website for a specific user.
    This endpoint combines data from multiple sources and formats it according to the requirements.
    
    Args:
        user_id (str): The ID of the user to fetch data for
        
    Returns:
        dict: Formatted portfolio data
    """
    user_id_str = str(user_id)
    
    # 1. Check in-memory Cache First (0 database queries, <5ms response time)
    if user_id_str in portfolio_cache:
        logger.info(f"Serving portfolio data for {user_id_str} from cache")
        return portfolio_cache[user_id_str]
        
    import time
    print(f"Starting to fetch data for user {user_id}")
    start_time = time.time()
    
    # Get the user's aggregated data from the materialized view
    portfolio_data = db.query(PortfolioMV).filter(PortfolioMV.user_id == user_id).first()
    
    if not portfolio_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Calculate total experience (optional: you could do this in JS, but keeping the python logic identical)
    # The 'experiences' field in our MV is a JSON array, so we parse it as dicts
    experiences_list = portfolio_data.experiences or []
    
    # Let's recreate the calculate_total_experience behavior with our dictionary representations
    experience_objects = [exp for exp in experiences_list if exp.get("type") == "experience"]
    total_experience_years = 0
    
    for exp in experience_objects:
        start_date = datetime.strptime(exp.get("start_date"), "%Y-%m-%d").date() if exp.get("start_date") else datetime.now().date()
        end_date = datetime.strptime(exp.get("end_date"), "%Y-%m-%d").date() if exp.get("end_date") else datetime.now().date()
        diff = relativedelta(end_date, start_date)
        years = diff.years + (diff.months / 12) + (diff.days / 365.25)
        total_experience_years += years
        
    floor_years = round(total_experience_years)
    if floor_years < 2:
        total_experience = floor_years
    elif total_experience_years > floor_years:
        total_experience = f"{floor_years}+"
    else:
        total_experience = str(floor_years)

    # Images are already in base64 format in the database
    avatar_base64 = portfolio_data.avatar
    about_dict = portfolio_data.about or {}
    about_image_base64 = about_dict.get('image')
    
    # Format experiences for timelineData
    timeline_data = []
    for exp in experiences_list:
        # Convert date strings to formatted strings
        start_date_obj = datetime.strptime(exp.get("start_date"), "%Y-%m-%d")
        
        if exp.get("end_date"):
            end_date_obj = datetime.strptime(exp.get("end_date"), "%Y-%m-%d")
            period = f"{start_date_obj.strftime('%b %Y')} - {end_date_obj.strftime('%b %Y')}"
        else:
            period = f"{start_date_obj.strftime('%b %Y')} - Present"
            
        item = {
            "id": exp.get("id"),
            "type": exp.get("type"),
            "title": exp.get("title"),
            "company": exp.get("company"),
            "period": period,
            "year": start_date_obj.year,
            "description": exp.get("description")
        }
        
        if exp.get("type") == "education":
            item["institution"] = item.pop("company")
            item["degree"] = item.pop("title")
        
        timeline_data.append(item)
    
    # Social links
    social_links = portfolio_data.social_links or []
    
    # Full featured skill details
    featured_skills = []
    featured_skill_ids = portfolio_data.featured_skill_ids or []
    if featured_skill_ids:
        featured_skills_data = db.query(Skill).filter(Skill.id.in_(featured_skill_ids)).all()
        featured_skills = [
            {
                "id": str(skill.id),
                "name": skill.name,
                "proficiency": skill.proficiency,
                "color": skill.color,
                "icon": skill.icon
            }
            for skill in featured_skills_data
        ]
    
    # Build the final response
    response = {
        "name": portfolio_data.name,
        "surname": portfolio_data.surname,
        "title": portfolio_data.title,
        "email": portfolio_data.email,
        "phone": portfolio_data.phone,
        "location": f"Based in {portfolio_data.location}" if portfolio_data.location else "",
        "availability": portfolio_data.availability,
        "avatar": avatar_base64,
        "heroStats": {
            "experience": total_experience
        },
        "socialLinks": social_links,
        "featuredSkills": featured_skills,
        "about": {
            "title": "More about",
            "highlight": "Myself",
            "subtitle": "About",
            "description": about_dict.get("description", ""),
            "shortdescription": about_dict.get("shortdescription", ""),
            "image": about_image_base64
        },
        "projectsSection": {
            "subtitle": "Projects",
            "title": "My",
            "highlight": "Projects"
        },
        "skillsSection": {
            "subtitle": "Skills",
            "title": "My",
            "highlight": "Skills"
        },
        "timelineSection": {
            "subtitle": "Experience & Education",
            "title": "My",
            "highlight": "Experience & Education"
        },
        "skillGroups": portfolio_data.skill_groups or [],
        "timelineData": timeline_data,
        "projectCategories": portfolio_data.project_categories or [],
        "projects": portfolio_data.projects or [],
        "reviews": portfolio_data.reviews or []
    }
    
    # Save the huge payload to the 24hr memory cache to bypass Postgres next time
    portfolio_cache[user_id_str] = response
    
    end_time = time.time()
    print(f"Time taken to fetch data for user {user_id}: {end_time - start_time}")
    
    return response

def clear_portfolio_cache(user_id: str):
    """
    Clears the public portfolio cache for a specific user.
    Called automatically by BaseRepository when the materialized view refreshes.
    """
    if str(user_id) in portfolio_cache:
        portfolio_cache.pop(str(user_id), None)
        logger.info(f"Cleared portfolio cache for user {user_id}")
