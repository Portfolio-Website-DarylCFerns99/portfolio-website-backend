from fastapi import APIRouter, HTTPException, Request, Depends
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.utils.sendgrid_utils import SendGridEmail
from app.dependencies.database import get_db
from app.models.user_model import User
from app.schemas.contact_schema import SocialLink, ContactRequest
from uuid import UUID
from app.config.settings import CORS_ORIGINS

router = APIRouter(tags=["Contact"])

@router.post("/contact/{user_id}")
async def send_contact_email(
    user_id: UUID,
    contact_data: ContactRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        email_sender = SendGridEmail()
        
        # Get the specific user from the database using user_id
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Use the frontend URL from settings instead of the backend URL
        portfolio_url = CORS_ORIGINS[0] if CORS_ORIGINS else None
        
        # Get social links from user data
        social_links = user.social_links if user.social_links else []
        
        # Get full name
        full_name = f"{user.name} {user.surname}" if user.name and user.surname else user.name or user.username
        
        # Send confirmation email to user
        email_sender.send_confirmation_email(
            name=contact_data.name,
            email=contact_data.email,
            subject=contact_data.subject,
            message=contact_data.message,
            social_links=social_links,
            portfolio_url=portfolio_url,
            your_name=full_name
        )
        
        # Send notification email to admin
        email_sender.send_notification_email(
            name=contact_data.name,
            email=contact_data.email,
            subject=contact_data.subject,
            message=contact_data.message,
            your_name=full_name
        )
        
        return {"message": "Emails sent successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 