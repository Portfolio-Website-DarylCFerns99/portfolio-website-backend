#!/usr/bin/env python3
"""
User Management Script

This script allows you to create, update, and delete users in the database.
It is meant to be run from the command line and is separate from the main application.

Usage:
    python manage_user.py create --email=<email> [--username=<username>] --password=<password>
    python manage_user.py update --id=<user_id> [--username=<username>] [--email=<email>] [--password=<password>]
    python manage_user.py delete --id=<user_id>
    python manage_user.py list
    python manage_user.py get --id=<user_id>
"""

import sys
import os
import argparse
import uuid
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

# Add parent directory to path so we can import our app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from our app
from app.models.base_model import Base
from app.models.user_model import User
from app.security.password import get_password_hash
from app.security.token import create_access_token

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Get database URL from environment or use a default
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logger.error("DATABASE_URL environment variable is not set")
    sys.exit(1)

# Create SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_user(email, password, username=None):
    """Create a new user in the database."""
    db = SessionLocal()
    try:
        # Use email as username if not provided
        if not username:
            username = email
        
        # Check if username already exists
        if db.query(User).filter(User.username == username).first():
            logger.error(f"User with username '{username}' already exists")
            return False
        
        # Check if email already exists
        if db.query(User).filter(User.email == email).first():
            logger.error(f"User with email '{email}' already exists")
            return False
        
        # Create new user
        hashed_password = get_password_hash(password)
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"User created successfully with ID: {user.id}")
        
        return True
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

def update_user(user_id, username=None, email=None, password=None):
    """Update an existing user in the database."""
    db = SessionLocal()
    try:
        # Find user by ID
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User with ID '{user_id}' not found")
            return False
        
        # Update fields if provided
        if username is not None:
            # Check if username is already taken by another user
            existing_user = db.query(User).filter(User.username == username).first()
            if existing_user and existing_user.id != user.id:
                logger.error(f"Username '{username}' is already taken")
                return False
            user.username = username
            
        if email is not None:
            # Check if email is already taken by another user
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user and existing_user.id != user.id:
                logger.error(f"Email '{email}' is already taken")
                return False
            user.email = email
            
            # If username was not provided, and we updated email, update username to match email
            if username is None:
                user.username = email
            
        if password is not None:
            user.hashed_password = get_password_hash(password)
        
        db.commit()
        logger.info(f"User with ID '{user_id}' updated successfully")
        return True
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

def delete_user(user_id):
    """Delete a user from the database."""
    db = SessionLocal()
    try:
        # Find user by ID
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User with ID '{user_id}' not found")
            return False
        
        db.delete(user)
        db.commit()
        logger.info(f"User with ID '{user_id}' deleted successfully")
        return True
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

def list_users():
    """List all users in the database."""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        if not users:
            logger.info("No users found in the database")
            return
        
        logger.info(f"Found {len(users)} users:")
        for user in users:
            logger.info(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")
        
        return users
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        return None
    finally:
        db.close()

def get_user(user_id):
    """Get a user by ID."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User with ID '{user_id}' not found")
            return None
        
        logger.info(f"User found: ID: {user.id}, Username: {user.username}, Email: {user.email}")
        # Generate a token for the user (useful for testing)
        token = create_access_token({"sub": str(user.id)})
        logger.info(f"Access token: {token}")
        
        return user
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        return None
    finally:
        db.close()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="User management CLI tool")
    subparsers = parser.add_subparsers(dest="action", help="Action to perform")
    
    # Create user parser
    create_parser = subparsers.add_parser("create", help="Create a new user")
    create_parser.add_argument("--username", help="User's username (optional, email will be used if not provided)")
    create_parser.add_argument("--email", required=True, help="User's email")
    create_parser.add_argument("--password", required=True, help="User's password")
    
    # Update user parser
    update_parser = subparsers.add_parser("update", help="Update an existing user")
    update_parser.add_argument("--id", required=True, help="User's ID (UUID)")
    update_parser.add_argument("--username", help="New username")
    update_parser.add_argument("--email", help="New email")
    update_parser.add_argument("--password", help="New password")
    
    # Delete user parser
    delete_parser = subparsers.add_parser("delete", help="Delete a user")
    delete_parser.add_argument("--id", required=True, help="User's ID (UUID)")
    
    # List users parser
    list_parser = subparsers.add_parser("list", help="List all users")
    
    # Get user parser
    get_parser = subparsers.add_parser("get", help="Get a user by ID")
    get_parser.add_argument("--id", required=True, help="User's ID (UUID)")
    
    return parser.parse_args()

def main():
    """Main function to handle user management based on command line arguments."""
    args = parse_args()
    
    if args.action == "create":
        success = create_user(args.email, args.password, args.username)
        sys.exit(0 if success else 1)
        
    elif args.action == "update":
        try:
            user_id = uuid.UUID(args.id)
        except ValueError:
            logger.error("Invalid UUID format for user ID")
            sys.exit(1)
            
        success = update_user(
            user_id,
            username=args.username,
            email=args.email,
            password=args.password
        )
        sys.exit(0 if success else 1)
        
    elif args.action == "delete":
        try:
            user_id = uuid.UUID(args.id)
        except ValueError:
            logger.error("Invalid UUID format for user ID")
            sys.exit(1)
            
        success = delete_user(user_id)
        sys.exit(0 if success else 1)
        
    elif args.action == "list":
        users = list_users()
        sys.exit(0 if users is not None else 1)
        
    elif args.action == "get":
        try:
            user_id = uuid.UUID(args.id)
        except ValueError:
            logger.error("Invalid UUID format for user ID")
            sys.exit(1)
            
        user = get_user(user_id)
        sys.exit(0 if user else 1)
        
    else:
        logger.error("No action specified. Use --help for available commands.")
        sys.exit(1)

if __name__ == "__main__":
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    main()
