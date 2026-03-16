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

logger = logging.getLogger(__name__)

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
    # Get the user by ID
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get all public skill groups and their skills
    skill_groups = db.query(SkillGroup).filter(SkillGroup.is_visible == True).all()
    
    # Get all public experiences (work and education)
    experiences = db.query(Experience).filter(Experience.is_visible == True).all()
    
    # Get all public project categories
    project_categories = db.query(ProjectCategory).filter(ProjectCategory.is_visible == True).all()
    
    # Get all public projects
    projects = db.query(Project).filter(Project.is_visible == True).all()
    
    # Get all public projects
    reviews = db.query(Review).filter(Review.is_visible == True).all()
    
    # Calculate total experience
    total_experience = calculate_total_experience(experiences)
    
    # Images are already in base64 format in the database
    avatar_base64 = user.avatar
    about_image_base64 = user.about.get('image') if user.about else None
    
    # Format experiences for timelineData
    timeline_data = []
    
    for exp in experiences:
        item = {
            "id": str(exp.id),
            "type": exp.type,
            "title": exp.title,
            "company": exp.organization,
            "period": f"{exp.start_date.strftime('%b %Y')} - {'Present' if not exp.end_date else exp.end_date.strftime('%b %Y')}",
            "year": exp.start_date.year,
            "description": exp.description
        }
        
        if exp.type == "education":
            # For education, rename fields to match expected format
            item["institution"] = item.pop("company")
            item["degree"] = item.pop("title")
        
        timeline_data.append(item)
    
    # Format skill groups
    formatted_skill_groups = []
    for group in skill_groups:
        # Check if skills is a JSON array or a relationship
        if hasattr(group, 'skills') and isinstance(group.skills, list):
            # It's JSON data
            skills_data = group.skills
        else:
            # It's a relationship
            skills_data = [
                {
                    "id": str(skill.id),
                    "name": skill.name,
                    "proficiency": skill.proficiency,
                    "color": skill.color,
                    "icon": skill.icon
                }
                for skill in group.skills if hasattr(skill, 'is_visible') and skill.is_visible
            ]
        
        formatted_group = {
            "name": group.name,
            "skills": skills_data
        }
        formatted_skill_groups.append(formatted_group)
    
    # Format projects - images are already in base64 format
    formatted_projects = []
    for project in projects:
        project_data = {
            "id": str(project.id),
            "type": project.type,
            "title": project.title,
            "description": project.description,
            "image": project.image,  # Already base64 encoded
            "tags": project.tags if project.tags else [],
            "url": project.url,
            "additional_data": project.additional_data,
            "created_at": project.created_at,
            "project_category_id": str(project.project_category_id)
        }
        formatted_projects.append(project_data)
    
    # Social links - Use the user's social links directly
    social_links = user.social_links if user.social_links else []
    
    # Get the user's featured skills if any
    featured_skill_ids = user.featured_skill_ids if user.featured_skill_ids else []
    
    # Get the full featured skill details if featured_skill_ids exist
    featured_skills = []
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
    
    # Build the final response according to the required format
    response = {
        "name": user.name,
        "surname": user.surname,
        "title": user.title,
        "email": user.email,
        "phone": user.phone,
        "location": f"Based in {user.location}" if user.location else "",
        "availability": user.availability,
        "avatar": avatar_base64,  # Already base64 encoded
        "heroStats": {
            "experience": total_experience
        },
        "socialLinks": social_links,
        "featuredSkills": featured_skills,
        "about": {
            "title": "More about",
            "highlight": "Myself",
            "subtitle": "About",
            "description": user.about.get("description") if user.about else "",
            "shortdescription": user.about.get("shortdescription") if user.about else "",
            "image": about_image_base64  # Already base64 encoded
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
        "skillGroups": formatted_skill_groups,
        "timelineData": timeline_data,
        "projectCategories": project_categories,
        "projects": formatted_projects,
        "reviews": reviews
    }
    
    return response
