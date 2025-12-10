# Google Cloud Platform Deployment (Backend)

This project includes a complete CI/CD pipeline using GitHub Actions for automated testing, building, and deployment to Google Cloud Platform.

> **IMPORTANT**: Before using this deployment method, you must rename the workflow file:
> Rename `.github/workflows/gcp-deploy.yml.bak` to `.github/workflows/gcp-deploy.yml`

## GitHub Workflow Features

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

## Settings Up GitHub Actions

### 1. Infrastructure Setup

**Before setting up GitHub Actions, you must create the required Google Cloud infrastructure using the dedicated infrastructure repository:**

👉 **[Portfolio Website Infrastructure Repository](https://github.com/Portfolio-Website-DarylCFerns99/portfolio-website-infrastructure)**

Follow the instructions in the infrastructure repository to create all required cloud resources before proceeding with the GitHub Actions setup.

### 2. Required GitHub Secrets

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

### 3. Service Account Setup

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

# Grant required permissions (Run individual gcloud projects add-iam-policy-binding commands as needed)
# ...
# Create and download key
gcloud iam service-accounts keys create key.json \
    --iam-account=$SA_EMAIL
```

### 4. Workflow Triggers

The workflow runs on:
- **Push to main branch**: Automatically deploys to production
- **Pull requests to main**: Runs tests and linting
- **Manual dispatch**: Can be triggered manually from GitHub Actions tab

## Monitoring Deployment

**Check deployment status:**
```bash
# View pods
kubectl get pods -l app=fastapi-app

# Check deployment status
kubectl rollout status deployment/fastapi-app

# View logs
kubectl logs -l app=fastapi-app --tail=100
```
