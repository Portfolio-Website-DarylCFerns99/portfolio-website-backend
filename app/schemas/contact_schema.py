from pydantic import BaseModel, EmailStr
from typing import Optional

class SocialLink(BaseModel):
    platform: str
    url: str
    tooltip: str
    icon: Optional[str] = None
    fileName: Optional[str] = None

class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str 