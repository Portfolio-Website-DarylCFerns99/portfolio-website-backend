# Portfolio Website Backend

![Python](https://img.shields.io/badge/python-v3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)
![GCP](https://img.shields.io/badge/GCP-Kubernetes-orange.svg)
<!-- ![Build Status](https://img.shields.io/github/actions/workflow/status/Portfolio-Website-DarylCFerns99/portfolio-website-backend/gcp-deploy.yml?branch=main) -->

A FastAPI MVC application for managing projects, reviews, experiences, and skills with JWT authentication, designed for portfolio websites with complete CI/CD automation.

## 🚀 Features

- **Project Management**: CRUD operations for portfolio projects with visibility control
- **Project Categories**: Classify projects into categories with visibility control
- **GitHub Integration**: Auto-fetch data for GitHub projects with daily refresh
- **Review System**: Create and manage testimonials with visibility control
- **Experience/Education**: Track work and educational history
- **Skills Management**: Organize skills into groups with proficiency levels
- **JWT Authentication**: Secure endpoints with token-based auth
- **Public/Private Routes**: Auth-required for admin, public access for visitors
- **UUID Primary Keys**: Enhanced security with UUID identifiers
- **Database Resilience**: Retry and rollback mechanisms
- **Contact Form Email**: SendGrid/Mailgun integration for contact form submissions with email notifications
- **AI Chatbot**: RAG-powered chatbot using Gemini for context-aware portfolio Q&A
- **Chat History**: Anonymous session persistence for chat interactions
- **Admin Chat Console**: Real-time view of user-bot interactions
- **Health Check**: Database connectivity monitoring endpoint
- **CI/CD Pipeline**: Automated testing, building, and deployment with GitHub Actions
- **Cloud Deployment**: Ready for Google Cloud Platform (GKE) deployment

Projects of type "github" will:
- Fetch repository data from GitHub when created
- Store complete GitHub API response in the `additional_data` field
- Have a 1-day expiration for the data
- Auto-refresh when accessed after expiration
- Can be manually refreshed via the refresh endpoint
- Support for private repositories (with proper GitHub token)

**GitHub API Features:**
- Repository metadata (stars, forks, language, description)
- README content extraction
- Repository statistics
- Automatic language detection

## 📁 Project Structure

```
portfolio-website-backend/
├── .github/                  # GitHub Actions workflows
├── app/
│   ├── config/               # App configuration
│   │   ├── database.py       # Database connection
│   │   └── settings.py       # App settings
│   ├── controllers/          # API endpoints
│   │   ├── project_controller.py
│   │   ├── project_category_controller.py
│   │   ├── review_controller.py
│   │   ├── experience_controller.py
│   │   ├── skill_controller.py
│   │   ├── user_controller.py
│   │   ├── contact_controller.py
│   │   └── chatbot_controller.py # Chatbot endpoints
│   ├── dependencies/         # FastAPI dependencies
│   │   ├── auth.py           # Authentication
│   │   └── database.py       # DB session
│   ├── jobs/                 # Background tasks
│   │   └── scheduler.py      # GitHub data refresh
│   ├── models/               # Database models
│   │   ├── base_model.py
│   │   ├── project_model.py
│   │   ├── project_category_model.py
│   │   ├── review_model.py
│   │   ├── experience_model.py
│   │   ├── skill_model.py
│   │   ├── user_model.py
│   │   ├── chat_model.py     # Chat sessions & messages
│   │   └── vector_store.py   # Vector embeddings
│   ├── repositories/         # Data access layer
│   │   ├── base_repository.py
│   │   ├── project_repository.py
│   │   ├── project_category_repository.py
│   │   ├── review_repository.py
│   │   ├── experience_repository.py
│   └── skill_repository.py
│   ├── schemas/              # Pydantic schemas
│   │   ├── project_schema.py
│   │   ├── project_category_schema.py
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
│   │   ├── project_category_service.py
│   │   ├── review_service.py
│   │   ├── experience_service.py
│   │   └── skill_service.py
│   │   └── vector_service.py # RAG & Embeddings logic
│   ├── templates/            # Email templates
│   │   └── emails/
│   │       ├── confirmation.html
│   │       └── notification.html
│   ├── utils/                # Utilities
│   │   ├── github_utils.py   # GitHub API integration
│   │   ├── mailgun_utils.py  # Mailgun Email functionality
│   │   ├── sendgrid_utils.py # Sendgrid Email functionality
│   │   ├── file_utils.py     # File handling utilities
│   │   ├── db_utils.py       # Database utilities
│   │   └── template_loader.py # Email template rendering
│   ├── __init__.py           # Package initialization
│   └── main.py               # App entry point
├── scripts/
│   └── manage_user.py        # CLI user management
├── alembic/                  # Database migrations
│   ├── versions/             # Migration files
│   ├── env.py               # Alembic environment
│   └── script.py.mako       # Migration template
├── alembic.ini               # Alembic configuration
├── Dockerfile                # Docker container configuration
├── .env                      # Environment variables (not in repo)
├── .gitignore                # Git ignore file
├── requirements.txt          # Project dependencies
├── LICENSE                   # MIT License
└── README.md                 # Project documentation
```

## 🔧 API Endpoints

### Authentication

- `POST /api/v1/users/login` - Login and get JWT token
- `GET /api/v1/users/profile` - Get user profile (requires auth)
- `PUT /api/v1/users/profile` - Update user profile (requires auth)

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

### Project Categories (Admin)

- `GET /api/v1/project-categories` - List all categories including hidden ones (requires auth)
- `POST /api/v1/project-categories` - Create a new category (requires auth)
- `GET /api/v1/project-categories/{id}` - Get a category by ID including if hidden (requires auth)
- `PUT /api/v1/project-categories/{id}` - Update a category (requires auth)

### Project Categories (Public)

- `GET /api/v1/project-categories/public` - List visible categories only (public access)

### Reviews (Admin)

- `GET /api/v1/reviews` - List all reviews including hidden ones (requires auth)
- `POST /api/v1/reviews` - Create a new review (requires auth)
- `GET /api/v1/reviews/{id}` - Get a specific review including if hidden (requires auth)
- `PATCH /api/v1/reviews/{id}/visibility` - Update review visibility (requires auth)
- `DELETE /api/v1/reviews/{id}` - Delete a review (requires auth)

### Reviews (Public)

- `GET /api/v1/reviews/public` - List visible reviews only (public access)

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

### Chatbot (Admin)

- `POST /api/v1/chatbot/sync` - Trigger RAG vector store synchronization (requires auth)
- `GET /api/v1/chatbot/sessions` - List chat sessions (requires auth)
- `GET /api/v1/chatbot/sessions/{session_id}/messages` - Get specific session history (requires auth)

### Chatbot (Public)

- `WS /api/v1/chatbot/ws/chat` - WebSocket endpoint for real-time chat

### System

- `GET /healthz` - Health check endpoint to verify API and database availability

## 👤 User Management

User management is handled via a CLI script rather than API endpoints for security:

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

## 🔐 Authentication

The API uses JWT tokens for authentication. To authenticate:

1. Obtain a token via the login endpoint or user management script
2. Include the token in the `Authorization` header:
   ```
   Authorization: Bearer <token>
   ```

**Token Configuration:**
- Default expiration: 120 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- Algorithm: HS256
- Secret key: Configurable via `JWT_SECRET_KEY` environment variable

## 👁️ Visibility Control

All content types (projects, reviews, experiences, skills) have visibility flags:
- `is_visible: true` - Item is publicly accessible
- `is_visible: false` - Item is hidden from public routes (still accessible via admin routes)

This enables you to hide items without deleting them, useful for:
- Content that you're not ready to make public
- Items that are still in development
- Content specific to certain audiences
- Content moderation
- Seasonal content

## 📧 Contact Form Email System

The API includes a complete contact form email system using SendGrid and Mailgun:

- **Contact Form Endpoint**: `POST /api/v1/contact/{user_id}` allows visitors to send messages
- **Dual Email System**:
  - Confirmation email sent to the visitor with a thank you message
  - Notification email sent to the portfolio owner with the visitor's message
- **HTML Email Templates**: Professional responsive email templates
- **Social Links Integration**: Your social links are automatically included in confirmation emails
- **Reply Functionality**: Easy one-click reply buttons in notification emails

To use this feature:

1. Set up a SendGrid/Mailgun account and get an API key
2. Add these variables to your `.env` file:
   ```
   SENDGRID_API_KEY/MAILGUN_API_KEY=your_sendgrid/mailgun_api_key
   SENDGRID_FROM_EMAIL/MAILGUN_FROM_EMAIL=your-verified@email.com
   SENDGRID_NOTIFICATION_TEMPLATE_ID/MAILGUN_NOTIFICATION_TEMPLATE_ID=your_notification_template_id
   SENDGRID_CONFIRMATION_TEMPLATE_ID/MAILGUN_CONFIRMATION_TEMPLATE_ID=your_confirmation_template_id
   ADMIN_EMAIL=your-admin@email.com
   ```

## ⚙️ Setup and Installation

### Prerequisites

- Python 3.12+
- PostgreSQL database (local or cloud)
- Git
- Docker (optional, for containerization)

### Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd portfolio-website-backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up a PostgreSQL database:**
   - **Option 1**: Install PostgreSQL locally
   - **Option 2**: Use [Neon](https://neon.tech/) - a serverless PostgreSQL service with a generous free tier that requires no credit card. Neon provides high-performance databases with automated scaling and branching capabilities.

5. **Set up environment variables:**
   ```bash
   cp env.example .env
   # On Windows: copy env.example .env
   ```

   Update the `.env` file with your configuration
   
   **Note**: For CORS_ORIGINS, you can specify multiple origins separated by commas, or use "*" to allow all origins (not recommended for production).

6. **Apply database migrations:**
   ```bash
   alembic upgrade head
   ```

   If you've made changes to the database models, generate a new migration:
   ```bash
   alembic revision --autogenerate -m "your migration message"
   alembic upgrade head
   ```

7. **Create at least one user:**
   ```bash
   python scripts/manage_user.py create --email=admin@example.com --password=secure123
   ```

8. **Start the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

9. **Access the API:**
   - API: `http://localhost:8000`
   - Documentation: `http://localhost:8000/docs`
   - Health Check: `http://localhost:8000/healthz`

## 🐳 Docker Deployment

### Building the Docker Image

```bash
# Build the image
docker build -t portfolio-backend .

# Run the container
docker run -p 8000:8000 --env-file .env portfolio-backend
```

### Docker Compose (Development)

Create a `docker-compose.yml` file:

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
    volumes:
      - .:/app
    command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: portfolio
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Run with:
```bash
docker-compose up -d
```

## 🚀 Deployment

### Render Deployment (Recommended)

1. **Create a New Web Service**
   - Go to [Render Dashboard](https://dashboard.render.com).
   - Click "New +" -> "Web Service".
   - Connect your GitHub repository.

2. **Configure Service**
   - **Environment**: Docker
   - **Branch**: main
   - **Region**: Choose closest to your users
   - **Plan**: Free (supports WebSockets!)

3. **Environment Variables**
   - Add all your production variables (see Environment Variables section).
   - Make sure to set `PORT=8000` (Render defaults to 10000).

4. **Deploy**
   - Click "Create Web Service".
   - Render will build and deploy your Docker container automatically.

### Alternative Deployment Methods

This project also supports deployment to Google Cloud Platform. Please refer to the detailed guide below:

-   **[Google Cloud Platform Deployment](DEPLOYMENT-GCP.md)**

## 🚀 Production Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in production environment
- [ ] Use a strong, unique `JWT_SECRET_KEY`
- [ ] Configure proper CORS origins (avoid `*` in production)
- [ ] Set up SSL/TLS certificates
- [ ] Configure proper database connection pooling
- [ ] Set up logging and monitoring
- [ ] Configure rate limiting
- [ ] Set up database backups
- [ ] Configure health check endpoints
- [ ] Set up error tracking (e.g., Sentry)

### Performance Optimization

**Database:**
- Use connection pooling
- Implement query optimization
- Set up database indices
- Configure read replicas if needed

**Application:**
- Use gunicorn or uvicorn with multiple workers
- Implement Redis for caching
- Set up CDN for static assets
- Configure gzip compression

## 📊 Monitoring and Logging

### Application Logging

The application uses Python's built-in logging module with structured logging:

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Application starting up...")
logger.error(f"Database connection error: {e}")
```

### Health Checks

- **Endpoint**: `GET /healthz`
- **Database Check**: Verifies database connectivity
- **Response Codes**: 200 (healthy), 503 (unhealthy)
- **Kubernetes Integration**: Used for readiness/liveness probes

### Metrics and Monitoring

Consider integrating:
- **Prometheus**: For metrics collection
- **Grafana**: For metrics visualization
- **Sentry**: For error tracking
- **ELK Stack**: For log aggregation

## 🔒 Security

### Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt for password security
- **CORS Configuration**: Configurable cross-origin resource sharing
- **Input Validation**: Pydantic schemas for request validation
- **UUID Primary Keys**: Enhanced security over sequential IDs
- **Environment Variables**: Sensitive data stored in environment variables

### Security Best Practices

- Keep dependencies updated
- Use HTTPS in production
- Implement rate limiting
- Regular security audits
- Secure database connections
- Validate all user inputs
- Implement proper error handling (don't expose sensitive information)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write comprehensive tests
- Update documentation for new features
- Use meaningful commit messages
- Keep pull requests focused and small

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

**Database Connection Issues:**
```bash
# Check database connectivity
psql $DATABASE_URL -c "SELECT 1;"

# Check environment variables
env | grep DATABASE_URL
```

**Migration Issues:**
```bash
# Check current migration status
alembic current

# View migration history
alembic history --verbose

# Reset to specific revision
alembic downgrade <revision_id>
```

**Docker Issues:**
```bash
# Build with no cache
docker build --no-cache -t portfolio-backend .

# Check container logs
docker logs <container_id>

# Debug container
docker run -it portfolio-backend /bin/sh
```

**GitHub Actions Issues:**
```bash
# Check workflow status
gh workflow list
gh run list

# View workflow logs
gh run view <run_id> --log
```

### Performance Issues

- Check database query performance
- Monitor memory usage
- Review API response times
- Check for N+1 queries
- Optimize database indices

### Support

For additional support:
1. Check the GitHub Issues page
2. Review the API documentation at `/docs`
3. Check application logs
4. Verify environment configuration
5. Test with minimal configuration

---

**Built with ❤️ using FastAPI, PostgreSQL, and modern DevOps practices**
