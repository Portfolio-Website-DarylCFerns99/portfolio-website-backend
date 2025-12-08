import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database settings
DATABASE_URL = os.getenv("DATABASE_URL", "")

# API settings
API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Retry settings
MAX_DB_RETRIES = int(os.getenv("MAX_DB_RETRIES", "3"))
RETRY_BACKOFF = float(os.getenv("RETRY_BACKOFF", "0.5"))

# Authentication settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "YOUR_DEFAULT_SECRET_KEY_CHANGE_THIS")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# # SendGrid settings
# SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
# SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "your-email@domain.com")
# ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "your-email@domain.com")
# SENDGRID_NOTIFICATION_TEMPLATE_ID = os.getenv("SENDGRID_NOTIFICATION_TEMPLATE_ID", "test-id")
# SENDGRID_CONFIRMATION_TEMPLATE_ID = os.getenv("SENDGRID_CONFIRMATION_TEMPLATE_ID", "test-id")

# MAILGUN settings
MAILGUN_API_URL = os.getenv("MAILGUN_API_URL", "")
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY", "")
MAILGUN_FROM_EMAIL = os.getenv("MAILGUN_FROM_EMAIL", "your-email@domain.com")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "your-email@domain.com")
MAILGUN_NOTIFICATION_TEMPLATE_ID = os.getenv("MAILGUN_NOTIFICATION_TEMPLATE_ID", "test-id")
MAILGUN_CONFIRMATION_TEMPLATE_ID = os.getenv("MAILGUN_CONFIRMATION_TEMPLATE_ID", "test-id")

# CORS settings
def get_cors_origins() -> List[str]:
    cors_origins = os.getenv("CORS_ORIGINS", "*")
    if cors_origins == "*":
        return ["*"]
    return [origin.strip() for origin in cors_origins.split(",") if origin.strip()]

CORS_ORIGINS = get_cors_origins()

# Create a settings class for compatibility, but using variables directly
class Settings:
    DATABASE_URL = DATABASE_URL
    API_PREFIX = API_PREFIX
    DEBUG = DEBUG
    MAX_DB_RETRIES = MAX_DB_RETRIES
    RETRY_BACKOFF = RETRY_BACKOFF
    CORS_ORIGINS = CORS_ORIGINS
    JWT_SECRET_KEY = JWT_SECRET_KEY
    ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES
    
    # SendGrid settings
    # SENDGRID_API_KEY = SENDGRID_API_KEY
    # SENDGRID_FROM_EMAIL = SENDGRID_FROM_EMAIL
    # ADMIN_EMAIL = ADMIN_EMAIL
    # SENDGRID_NOTIFICATION_TEMPLATE_ID = SENDGRID_NOTIFICATION_TEMPLATE_ID
    # SENDGRID_CONFIRMATION_TEMPLATE_ID = SENDGRID_CONFIRMATION_TEMPLATE_ID
    
    # Mailgun settings
    MAILGUN_API_URL = MAILGUN_API_URL
    MAILGUN_API_KEY = MAILGUN_API_KEY
    MAILGUN_FROM_EMAIL = MAILGUN_FROM_EMAIL
    ADMIN_EMAIL = ADMIN_EMAIL
    MAILGUN_NOTIFICATION_TEMPLATE_ID = MAILGUN_NOTIFICATION_TEMPLATE_ID
    MAILGUN_CONFIRMATION_TEMPLATE_ID = MAILGUN_CONFIRMATION_TEMPLATE_ID

    # LLM settings
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

settings = Settings()
