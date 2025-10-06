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
- **Health Check**: Database connectivity monitoring endpoint
- **CI/CD Pipeline**: Automated testing, building, and deployment with GitHub Actions
- **Cloud Deployment**: Ready for Google Cloud Platform (GKE) deployment

## 📁 Project Structure

```
portfolio-website-backend/
├── .github/                  # GitHub Actions workflows
│   └── workflows/
│       └── gcp-deploy.yml    # CI/CD pipeline configuration
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
│   │   └── contact_controller.py
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
│   │   └── user_model.py
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

5. **Create a `.env` file:**
   ```env
   DATABASE_URL=postgresql://user:password@localhost/dbname
   API_PREFIX=/api/v1
   DEBUG=True
   MAX_DB_RETRIES=3
   RETRY_BACKOFF=0.5
   JWT_SECRET_KEY=your_super_secret_key_change_this_in_production
   ACCESS_TOKEN_EXPIRE_MINUTES=120
   GITHUB_TOKEN=your_github_token  # Optional, for GitHub API
   CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
   MAILGUN_API_KEY=your_mailgun_api_key  # For email functionality
   MAILGUN_FROM_EMAIL=your-verified@email.com
   MAILGUN_NOTIFICATION_TEMPLATE_ID=your_notification_template_id
   MAILGUN_CONFIRMATION_TEMPLATE_ID=your_confirmation_template_id
   ADMIN_EMAIL=your-admin@email.com
   ```
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

## 🚀 CI/CD with GitHub Actions

This project includes a complete CI/CD pipeline using GitHub Actions for automated testing, building, and deployment to Google Cloud Platform.

### GitHub Workflow Features

The `.github/workflows/gcp-deploy.yml` workflow provides:

- **Continuous Integration**:
  - Automated testing on push/PR to main branch
  - Python dependency caching
  - Code linting with flake8
  - Manual workflow dispatch

- **Continuous Deployment**:
  - Docker image building and pushing to Google Container Registry (GCR)
  - Kubernetes deployment to Google Kubernetes Engine (GKE)
  - Network Endpoint Group (NEG) management for load balancing
  - Health check integration
  - Rollback capabilities

### Setting Up GitHub Actions

#### 1. Infrastructure Setup

**Before setting up GitHub Actions, you must create the required Google Cloud infrastructure using the dedicated infrastructure repository:**

👉 **[Portfolio Website Infrastructure Repository](https://github.com/Portfolio-Website-DarylCFerns99/portfolio-website-infrastructure)**

This repository contains Terraform configurations to automatically provision:
- Google Kubernetes Engine (GKE) cluster
- Network Endpoint Groups (NEGs)
- Load balancers and networking components
- IAM roles and permissions
- Artifact Registry repositories

Follow the instructions in the infrastructure repository to create all required cloud resources before proceeding with the GitHub Actions setup.

#### 2. Required GitHub Secrets

Configure these secrets in your GitHub repository (`Settings > Secrets and variables > Actions`):

```bash
# Google Cloud Platform
GCP_SA_KEY              # Service account JSON key (base64 encoded)
GCP_PROJECT_ID          # Your GCP project ID
GCP_REGION              # GCP region (e.g., us-central1)
GCP_ZONE                # GCP zone (e.g., us-central1-a)
GKE_CLUSTER_NAME        # Your GKE cluster name

# Kubernetes
K8S_NAMESPACE           # Kubernetes namespace (e.g., default)
DEPLOYMENT_NAME         # Deployment name (e.g., fastapi-app)
GCP_BACKEND_PORT        # Backend port (8000)

# Application
ENV_FILE                # Complete .env file content for production
```

#### 3. Service Account Setup

Create a service account with the following permissions for GitHub Actions deployment:

**Required IAM Roles:**
- **Artifact Registry Create-on-Push Writer** - `roles/artifactregistry.createOnPushWriter`
- **Artifact Registry Writer** - `roles/artifactregistry.writer`  
- **Compute Admin** - `roles/compute.admin`
- **Kubernetes Engine Admin** - `roles/container.admin`
- **Service Account User** - `roles/iam.serviceAccountUser`
- **Storage Admin** - `roles/storage.admin`

```bash
# Create service account
gcloud iam service-accounts create github-actions \
    --description="Service account for GitHub Actions" \
    --display-name="GitHub Actions"

# Get the service account email
SA_EMAIL="github-actions@YOUR_PROJECT_ID.iam.gserviceaccount.com"

# Grant required permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/artifactregistry.createOnPushWriter"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/compute.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/container.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/storage.admin"

# Create and download key
gcloud iam service-accounts keys create key.json \
    --iam-account=$SA_EMAIL
```

#### 4. Workflow Triggers

The workflow runs on:
- **Push to main branch**: Automatically deploys to production
- **Pull requests to main**: Runs tests and linting
- **Manual dispatch**: Can be triggered manually from GitHub Actions tab

#### 5. Deployment Process

1. **Code Quality Checks**:
   ```bash
   # Lint with flake8
   flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
   ```

2. **Docker Build & Push**:
   ```bash
   # Build with commit SHA tag
   docker build -t gcr.io/PROJECT_ID/fastapi-app:COMMIT_SHA .
   docker push gcr.io/PROJECT_ID/fastapi-app:COMMIT_SHA
   ```

3. **Kubernetes Deployment**:
   ```bash
   # Update deployment image
   kubectl set image deployment/fastapi-app api=gcr.io/PROJECT_ID/fastapi-app:NEW_TAG
   kubectl rollout status deployment/fastapi-app --timeout=180s
   ```

4. **Health Check**: The deployment includes readiness probes that check the `/healthz` endpoint

#### 6. Monitoring Deployment

**Check deployment status:**
```bash
# View pods
kubectl get pods -l app=fastapi-app

# Check deployment status
kubectl rollout status deployment/fastapi-app

# View logs
kubectl logs -l app=fastapi-app --tail=100
```

**Access the application:**
```bash
# Port forward for testing
kubectl port-forward deployment/fastapi-app 8000:8000

# Or set up an ingress/load balancer
```

### Workflow Configuration Details

The workflow includes several advanced features:

- **Environment Management**: Production environment variables are injected via GitHub secrets
- **Caching**: Python dependencies are cached to speed up builds
- **Error Handling**: Continues on lint errors but fails on build/deploy errors
- **Resource Management**: Kubernetes deployment includes resource limits and requests
- **Rolling Updates**: Zero-downtime deployments with health checks
- **NEG Management**: Automatically manages Network Endpoint Groups for load balancing

## 🔧 GitHub Integration

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

### Environment Variables for Production

```env
DATABASE_URL=postgresql://user:secure_password@prod-db:5432/portfolio_prod
DEBUG=False
JWT_SECRET_KEY=your_super_secure_production_key_here
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
SENDGRID_API_KEY/MAILGUN_API_KEY=your_production_sendgrid/mailgun_key
SENDGRID_FROM_EMAIL/MAILGUN_FROM_EMAIL=noreply@yourdomain.com
ADMIN_EMAIL=admin@yourdomain.com
```

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
