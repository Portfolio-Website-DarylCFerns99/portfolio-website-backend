# Portfolio Website Backend

A FastAPI MVC application for managing projects, reviews, experiences, and skills with JWT authentication.

## Features

- **Project Management**: CRUD operations for portfolio projects with visibility control
- **GitHub Integration**: Auto-fetch data for GitHub projects with daily refresh
- **Review System**: Create and manage testimonials with visibility control
- **Experience/Education**: Track work and educational history
- **Skills Management**: Organize skills into groups with proficiency levels
- **JWT Authentication**: Secure endpoints with token-based auth
- **Public/Private Routes**: Auth-required for admin, public access for visitors
- **UUID Primary Keys**: Enhanced security with UUID identifiers
- **Database Resilience**: Retry and rollback mechanisms
- **Contact Form Email**: SendGrid integration for contact form submissions with email notifications
- **Health Check**: Database connectivity monitoring endpoint

## Project Structure

```
portfolio-website-backend/
├── app/
│   ├── config/               # App configuration
│   │   ├── database.py       # Database connection
│   │   └── settings.py       # App settings
│   ├── controllers/          # API endpoints
│   │   ├── project_controller.py
│   │   ├── review_controller.py
│   │   ├── experience_controller.py
│   │   ├── skill_controller.py
│   │   ├── user_controller.py
│   │   └── contact_controller.py
│   ├── dependencies/         # FastAPI dependencies
│   │   ├── auth.py           # Authentication
│   │   └── database.py       # DB session
│   ├── jobs/                 # Background tasks
│   │   └── scheduler.py      # GitHub data refresh
│   ├── models/               # Database models
│   │   ├── base_model.py
│   │   ├── project_model.py
│   │   ├── review_model.py
│   │   ├── experience_model.py
│   │   ├── skill_model.py
│   │   └── user_model.py
│   ├── repositories/         # Data access layer
│   │   ├── base_repository.py
│   │   ├── project_repository.py
│   │   ├── review_repository.py
│   │   ├── experience_repository.py
│   │   └── skill_repository.py
│   ├── schemas/              # Pydantic schemas
│   │   ├── project_schema.py
│   │   ├── review_schema.py
│   │   ├── experience_schema.py
│   │   ├── skill_schema.py
│   │   ├── user_schema.py
│   │   └── contact_schema.py
│   ├── security/             # Auth components
│   │   ├── password.py       # Password hashing
│   │   └── token.py          # JWT functionality
│   ├── services/             # Business logic
│   │   ├── project_service.py
│   │   ├── review_service.py
│   │   ├── experience_service.py
│   │   └── skill_service.py
│   ├── templates/            # Email templates
│   │   └── emails/
│   │       ├── confirmation.html
│   │       └── notification.html
│   ├── utils/                # Utilities
│   │   ├── github_utils.py   # GitHub API integration
│   │   ├── sendgrid_utils.py # Email functionality
│   │   └── template_loader.py # Email template rendering
│   ├── __init__.py           # Package initialization
│   └── main.py               # App entry point
├── scripts/
│   └── manage_user.py        # CLI user management
├── alembic/                  # Database migrations
├── alembic.ini               # Alembic configuration
├── .env                      # Environment variables
├── .gitignore                # Git ignore file
├── requirements.txt          # Project dependencies
├── LICENSE                   # MIT License
└── README.md                 # Project documentation
```

## API Endpoints

### Authentication

- `POST /api/v1/users/login` - Login and get JWT token
- `GET /api/v1/users/profile` - Get user profile (requires auth)
- `PUT /api/v1/users/profile` - Update user profile (requires auth)`

### Projects (Admin)

- `GET /api/v1/projects` - List all projects including hidden ones (requires auth)
- `POST /api/v1/projects` - Create a new project (requires auth)
- `GET /api/v1/projects/{id}` - Get a specific project including if hidden (requires auth)
- `PUT /api/v1/projects/{id}` - Update a project (requires auth)
- `PATCH /api/v1/projects/{id}/visibility` - Update project visibility (requires auth)
- `DELETE /api/v1/projects/{id}` - Delete a project (requires auth)
- `POST /api/v1/projects/{id}/refresh` - Refresh GitHub data (requires auth)

### Projects (Public)

- `GET /api/v1/projects/public` - List visible projects only (public access)
- `GET /api/v1/projects/public/{id}` - Get a specific visible project (public access)

### Reviews (Admin)

- `GET /api/v1/reviews` - List all reviews including hidden ones (requires auth)
- `POST /api/v1/reviews` - Create a new review (requires auth)
- `GET /api/v1/reviews/{id}` - Get a specific review including if hidden (requires auth)
- `PATCH /api/v1/reviews/{id}/visibility` - Update review visibility (requires auth)
- `DELETE /api/v1/reviews/{id}` - Delete a review (requires auth)

### Reviews (Public)

- `GET /api/v1/reviews/public` - List visible reviews only (public access)
- `GET /api/v1/reviews/public/{id}` - Get a specific visible review (public access)

### Experiences/Education (Admin)

- `GET /api/v1/experiences` - List all experiences/education including hidden ones (requires auth)
- `POST /api/v1/experiences` - Create a new experience/education entry (requires auth)
- `GET /api/v1/experiences/{id}` - Get a specific experience/education entry including if hidden (requires auth)
- `PUT /api/v1/experiences/{id}` - Update an experience/education entry (requires auth)
- `PATCH /api/v1/experiences/{id}/visibility` - Update experience/education visibility (requires auth)
- `DELETE /api/v1/experiences/{id}` - Delete an experience/education entry (requires auth)

### Experiences/Education (Public)

- `GET /api/v1/experiences/public` - List visible experiences/education only (public access)
- `GET /api/v1/experiences/public/{id}` - Get a specific visible experience/education entry (public access)

### Skills (Admin)

- `GET /api/v1/skills/groups` - List all skill groups including hidden ones (requires auth)
- `POST /api/v1/skills/groups` - Create a new skill group (requires auth)
- `GET /api/v1/skills/groups/{id}` - Get a specific skill group including if hidden (requires auth)
- `PUT /api/v1/skills/groups/{id}` - Update a skill group (requires auth)
- `PATCH /api/v1/skills/groups/{id}/visibility` - Update skill group visibility (requires auth)
- `DELETE /api/v1/skills/groups/{id}` - Delete a skill group (requires auth)

### Skills (Public)

- `GET /api/v1/skills/groups/public` - List visible skill groups only (public access)

### Contact

- `POST /api/v1/contact/{user_id}` - Send contact form emails (public access)

### System

- `GET /healthz` - Health check endpoint to verify API and database availability

## Models

### Project Model
- UUID primary key
- Title and description
- Type (github or custom)
- GitHub metadata and expiry for automatic updates
- Base64 image data
- Tags array
- Additional_data field with complete GitHub API response
- Visibility flag (to show/hide projects)

### Review Model
- UUID primary key
- Name of reviewer
- Rating
- Content (testimonial text)
- Where the reviewer knows you from
- Visibility flag (to show/hide reviews)

### Experience Model
- UUID primary key
- Type (experience or education)
- Title (job title or degree)
- Organization (company or institution)
- Start date and end date (end date can be null for current positions)
- Description
- Visibility flag (to show/hide entries)

### Skill Group Model
- UUID primary key
- Name (e.g., "Frontend", "Programming Languages")
- Skills array (name, proficiency level, icon, color)
- Visibility flag (to show/hide skills)

### User Model
- UUID primary key
- Username
- Email
- Hashed password
- Optional profile fields including:
  - Name, surname, title, phone, location, availability
  - Avatar (base64 encoded image)
  - Social links (including support for file uploads like resumes)
  - About section

## User Management

User management is handled via a CLI script rather than API endpoints:

```bash
# Create a user
python scripts/manage_user.py create --email=admin@example.com --password=secure123 [--username=admin]

# Update a user
python scripts/manage_user.py update --id=<uuid> --email=new@example.com --password=newpass

# Delete a user
python scripts/manage_user.py delete --id=<uuid>

# List users
python scripts/manage_user.py list

# Get a user (and generate a token)
python scripts/manage_user.py get --id=<uuid>
```

## Authentication

The API uses JWT tokens for authentication. To authenticate:

1. Obtain a token via the login endpoint or user management script
2. Include the token in the `Authorization` header:
   ```
   Authorization: Bearer <token>
   ```

## Visibility Control

All content types (projects, reviews, experiences, skills) have visibility flags:
- `is_visible: true` - Item is publicly accessible
- `is_visible: false` - Item is hidden from public routes (still accessible via admin routes)

## File Uploads in Social Links

The API now supports document uploads (e.g., resumes, CVs) in social links through base64-encoded file data.

### Pure JSON User Profile Update

The user profile update endpoint (`PUT /api/v1/users/profile`) has been simplified to use a pure JSON approach:

- No FormData or file uploads required
- Files are converted to base64 on the frontend
- Base64 data is sent directly in the `url` field of document-type social links

This approach provides a clean, straightforward API that supports all profile updates including document attachments.

See the [User Profile Update Documentation](./docs/user_profile_update.md) for details on how to implement this feature in your frontend.

This enables you to hide items without deleting them, useful for:
- Content that you're not ready to make public
- Items that are still in development
- Content specific to certain audiences
- Content moderation
- Seasonal content

## Contact Form Email System

The API includes a complete contact form email system using SendGrid:

- **Contact Form Endpoint**: `POST /api/v1/contact/{user_id}` allows visitors to send messages
- **Dual Email System**:
  - Confirmation email sent to the visitor with a thank you message
  - Notification email sent to the portfolio owner with the visitor's message
- **HTML Email Templates**: Professional responsive email templates
- **Social Links Integration**: Your social links are automatically included in confirmation emails
- **Reply Functionality**: Easy one-click reply buttons in notification emails

To use this feature:

1. Set up a SendGrid account and get an API key
2. Add these variables to your `.env` file:
   ```
   SENDGRID_API_KEY=your_sendgrid_api_key
   SENDGRID_FROM_EMAIL=your-verified@email.com
   ADMIN_EMAIL=your-admin@email.com
   ```

## Setup and Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd portfolio-website-backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up a PostgreSQL database:
   - Option 1: Install PostgreSQL locally
   - Option 2: Use [Neon](https://neon.tech/) - a serverless PostgreSQL service with a generous free tier that requires no credit card. Neon provides high-performance databases with automated scaling and branching capabilities.

5. Create a `.env` file with the following variables:
   ```
   DATABASE_URL=postgresql://user:password@localhost/dbname
   API_PREFIX=/api/v1
   DEBUG=True
   JWT_SECRET_KEY=your_secret_key
   ACCESS_TOKEN_EXPIRE_MINUTES=120
   GITHUB_TOKEN=your_github_token  # Optional, for GitHub API
   CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
   SENDGRID_API_KEY=your_sendgrid_api_key  # For email functionality
   SENDGRID_FROM_EMAIL=your-verified@email.com
   ADMIN_EMAIL=your-admin@email.com
   ```
   Note: For CORS_ORIGINS, you can specify multiple origins separated by commas, or use "*" to allow all origins.

6. Apply the database migrations:
   ```
   alembic upgrade head
   ```

   If you've made changes to the database models, generate a new migration:
   ```
   alembic revision --autogenerate -m "your migration message"
   ```
   Then apply the new migration with `alembic upgrade head`.

7. Create at least one user using the management script:
   ```
   python scripts/manage_user.py create --email=admin@example.com --password=secure123
   ```

8. Start the application:
   ```
   uvicorn app.main:app --reload
   ```

9. API documentation is available at `http://localhost:8000/docs`

## GitHub Integration

Projects of type "github" will:
- Fetch repository data from GitHub when created
- Store complete GitHub API response in the additional_data field
- Have a 1-day expiration for the data
- Auto-refresh when accessed after expiration
- Can be manually refreshed via the refresh endpoint

## Development and Deployment

### Development

```bash
# Run with hot reload
uvicorn app.main:app --reload
```

### Production

```bash
# Run in production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

For production deployment, consider:
- Using a proper WSGI server (Gunicorn)
- Setting up a reverse proxy (Nginx)
- Configuring proper CORS settings
- Using a secure JWT secret key
- Implementing rate limiting

## License

This project is licensed under the MIT License - see the LICENSE file for details.
