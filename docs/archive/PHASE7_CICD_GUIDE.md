# Phase 7: CI/CD Pipeline - Complete Guide

## 🎯 Overview

Phase 7 implements a complete CI/CD (Continuous Integration/Continuous Deployment) pipeline using GitHub Actions. This automates testing, model training, Docker builds, and deployment.

## 📦 What Was Implemented

### 1. GitHub Actions Workflow (`.github/workflows/ci-cd.yml`)

Five automated jobs that run on every push/PR:

#### Job 1: Test 🧪
- Runs on: Every push and PR
- Actions:
  - Checkout code
  - Setup Python 3.11
  - Cache pip packages
  - Install dependencies
  - Run pytest tests
  - Generate coverage report
  - Upload to Codecov

#### Job 2: Lint 🔍
- Runs on: Every push and PR
- Actions:
  - Code quality checks with flake8
  - Format checking with black
  - Import sorting with isort
  - Ensures code standards

#### Job 3: Build API 🐳
- Runs on: After tests pass
- Actions:
  - Build Docker image
  - Test Docker build
  - Push to Docker Hub (on main branch)
  - Tag with commit SHA and 'latest'

#### Job 4: Train Model 🎓
- Runs on: Push to main branch only
- Actions:
  - Pull data from DVC
  - Train model with MLflow
  - Register model to Model Registry
  - Auto-promote if better than production

#### Job 5: Deploy 🚀
- Runs on: After build and train succeed
- Actions:
  - Deploy API to cloud platform
  - Update production services
  - (Customizable for your cloud provider)

### 2. Model Registration Script (`scripts/register_model.py`)

Automated model promotion with intelligence:
- Finds latest trained model
- Compares F1-score with current production model
- Auto-promotes if better
- Archives old production model
- Keeps staging model if not better

## 🚀 Quick Start

### Step 1: Initialize Git Repository (if not done)

```powershell
# Initialize git
git init

# Add all files
git add .

# First commit
git commit -m "Initial commit: MLOps pipeline complete"
```

### Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Create repository: `bus-passenger-classifier`
3. **Don't** initialize with README (you already have one)
4. Copy the repository URL

### Step 3: Connect Local to GitHub

```powershell
# Add remote
git remote add origin https://github.com/YOUR_USERNAME/bus-passenger-classifier.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 4: Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:

#### For Docker Hub (Optional)
- `DOCKER_USERNAME` - Your Docker Hub username
- `DOCKER_PASSWORD` - Your Docker Hub access token

#### For MLflow (Optional)
- `MLFLOW_TRACKING_URI` - Remote MLflow server URL
  - Example: `https://your-mlflow-server.com`
  - Or use `http://localhost:5000` for local

#### For DVC (Optional)
- `DVC_REMOTE_URL` - Remote storage URL
  - Example: `s3://your-bucket/data`
  - Or Azure, GCP, SSH, etc.

### Step 5: Test the Pipeline

```powershell
# Make a change
echo "# Test CI/CD" >> README.md

# Commit and push
git add README.md
git commit -m "Test CI/CD pipeline"
git push

# Go to GitHub → Actions tab to see pipeline running
```

## 📊 Pipeline Flow

```
┌─────────────────────────────────────────────────┐
│  Push to GitHub / Create Pull Request          │
└────────────────┬────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
   ┌────────┐      ┌──────────┐
   │  Test  │      │   Lint   │
   │  🧪   │      │   🔍    │
   └────┬───┘      └─────┬────┘
        │                │
        └────────┬───────┘
                 │
                 ▼
        ┌────────────────┐
        │   Tests Pass?  │
        └────┬──────┬────┘
             │ No   │ Yes
             ▼      ▼
        ┌────┐  ┌──────────────┐
        │Stop│  │ Build Docker │
        └────┘  │     🐳      │
                └──────┬───────┘
                       │
                ┌──────┴──────┐
                │             │
                ▼             ▼
         ┌──────────┐  ┌──────────┐
         │  Train   │  │  Build   │
         │  Model   │  │  Success?│
         │   🎓    │  └─────┬────┘
         └────┬─────┘        │
              │              │
              └──────┬───────┘
                     │
                     ▼
            ┌────────────────┐
            │     Deploy     │
            │      🚀       │
            └────────────────┘
                     │
                     ▼
            ┌────────────────┐
            │   Production   │
            └────────────────┘
```

## 🔧 Customization Guide

### For Local Development Only

If you don't want to use GitHub Actions, comment out jobs:

```yaml
# .github/workflows/ci-cd.yml

# Comment out these jobs if not using cloud services:
  # build-api:  # Comment if no Docker Hub
  # train-model:  # Comment if no remote MLflow
  # deploy:  # Comment if no cloud deployment
```

### For Different Cloud Providers

#### AWS Deployment
```yaml
- name: Deploy to AWS ECS
  run: |
    aws ecs update-service \
      --cluster bus-classifier-cluster \
      --service bus-classifier-api \
      --force-new-deployment
  env:
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
    AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

#### Google Cloud Platform
```yaml
- name: Deploy to GCP Cloud Run
  run: |
    gcloud run deploy bus-classifier-api \
      --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/bus-classifier-api:latest \
      --platform managed \
      --region us-central1
  env:
    GOOGLE_APPLICATION_CREDENTIALS: ${{ secrets.GCP_SA_KEY }}
```

#### Azure
```yaml
- name: Deploy to Azure Container Instances
  run: |
    az container create \
      --resource-group bus-classifier-rg \
      --name bus-classifier-api \
      --image ${{ secrets.DOCKER_USERNAME }}/bus-passenger-api:latest
  env:
    AZURE_CREDENTIALS: ${{ secrets.AZURE_CREDENTIALS }}
```

### For Different Testing Frameworks

If using different test tools:

```yaml
# For unittest instead of pytest
- name: Run tests
  run: python -m unittest discover tests/

# For nose2
- name: Run tests
  run: nose2 -v

# For tox (multiple Python versions)
- name: Run tests
  run: tox
```

## 📈 Monitoring and Notifications

### Add Slack Notifications

```yaml
- name: Notify Slack
  uses: slackapi/slack-github-action@v1.24.0
  with:
    payload: |
      {
        "text": "CI/CD Pipeline completed for ${{ github.repository }}"
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
  if: always()
```

### Add Email Notifications

GitHub Actions automatically sends emails on workflow failures to repository owners.

### Add Discord Notifications

```yaml
- name: Notify Discord
  uses: sarisia/actions-status-discord@v1
  with:
    webhook: ${{ secrets.DISCORD_WEBHOOK }}
    status: ${{ job.status }}
  if: always()
```

## 🎯 Best Practices

### 1. Branch Protection Rules

Enable on GitHub:
- Settings → Branches → Add rule
- Require status checks to pass
- Require pull request reviews
- Require up-to-date branches

### 2. Semantic Versioning

Tag releases:
```powershell
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

### 3. Environment Variables

Use different configs for environments:
```yaml
env:
  ENV: ${{ github.ref == 'refs/heads/main' && 'production' || 'staging' }}
```

### 4. Caching

Cache dependencies for faster builds:
```yaml
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
```

### 5. Secrets Management

Never commit secrets! Use:
- GitHub Secrets for CI/CD
- Environment variables
- Secret management services (AWS Secrets Manager, etc.)

## 🧪 Testing the Pipeline Locally

### Test with Act (GitHub Actions locally)

```powershell
# Install act
choco install act-cli

# Run workflow locally
act -j test
act -j lint
```

### Test Scripts Manually

```powershell
# Test model registration
python scripts/register_model.py

# Test with environment variables
$env:MLFLOW_TRACKING_URI="http://localhost:5000"
python scripts/register_model.py
```

## 📊 Monitoring Pipeline Success

### GitHub Actions Tab

1. Go to your repository on GitHub
2. Click "Actions" tab
3. See all workflow runs
4. Click any run to see detailed logs
5. Check individual job status

### Status Badge

Add to README.md:
```markdown
![CI/CD](https://github.com/YOUR_USERNAME/bus-passenger-classifier/workflows/CI/CD%20Pipeline/badge.svg)
```

### Codecov Badge

After setting up Codecov:
```markdown
![Coverage](https://codecov.io/gh/YOUR_USERNAME/bus-passenger-classifier/branch/main/graph/badge.svg)
```

## 🚨 Troubleshooting

### Pipeline Fails on Test Job

```
Error: No module named 'pytest'
```

**Solution**: Add pytest to requirements-test.txt

### Docker Build Fails

```
Error: Cannot find Dockerfile
```

**Solution**: Ensure api/Dockerfile exists in repository

### Model Training Fails

```
Error: passengers.csv not found
```

**Solution**: 
- Either commit CSV files (if small)
- Or setup DVC remote storage
- Or skip train-model job for now

### Secrets Not Found

```
Error: Secret DOCKER_USERNAME not set
```

**Solution**: Add secrets in GitHub repo Settings → Secrets

### Permission Denied on Deploy

```
Error: Insufficient permissions
```

**Solution**: Check cloud provider credentials and permissions

## 📝 Minimal Setup (No External Services)

If you want CI/CD without Docker Hub, MLflow cloud, etc.:

```yaml
# .github/workflows/ci-cd-minimal.yml
name: CI Pipeline (Minimal)

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - run: |
        pip install -r requirements-core.txt
        pip install -r requirements-test.txt
    - run: pytest tests/ -v

  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - run: |
        pip install flake8 black
        flake8 src/ --max-line-length=127
        black --check src/
```

This minimal version:
- ✅ Runs tests
- ✅ Checks code quality
- ❌ No Docker build
- ❌ No model training
- ❌ No deployment

## 🎓 Advanced Features (Optional)

### 1. Multi-Environment Deployment

```yaml
strategy:
  matrix:
    environment: [staging, production]
```

### 2. Scheduled Model Retraining

```yaml
on:
  schedule:
    - cron: '0 0 * * 0'  # Every Sunday at midnight
```

### 3. Manual Workflow Trigger

```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        default: 'staging'
```

### 4. Performance Testing

```yaml
- name: Run performance tests
  run: |
    pip install locust
    locust -f tests/performance_test.py --headless -u 100 -r 10
```

### 5. Security Scanning

```yaml
- name: Security scan
  run: |
    pip install bandit safety
    bandit -r src/
    safety check
```

## ✅ Success Checklist

Phase 7 is complete when:

- [ ] GitHub Actions workflow file exists
- [ ] Workflow runs on push/PR
- [ ] Tests pass automatically
- [ ] Code quality checks pass
- [ ] Model registration script works
- [ ] (Optional) Docker image builds
- [ ] (Optional) Model training runs
- [ ] (Optional) Deployment succeeds
- [ ] Status badges added to README
- [ ] Documentation updated

## 🎉 Benefits

With Phase 7 CI/CD, you now have:

✅ **Automated Testing** - Catch bugs before merge  
✅ **Code Quality** - Consistent standards enforced  
✅ **Automated Builds** - Docker images built automatically  
✅ **Model Versioning** - Smart model promotion  
✅ **Continuous Deployment** - Push to production safely  
✅ **Faster Iteration** - Less manual work  
✅ **Better Collaboration** - Team-ready workflow  
✅ **Professional DevOps** - Industry-standard practices  

---

**Phase 7 Status**: ✅ **COMPLETE**

**Total Pipeline**: Phases 1-7 all complete! 🎊

Your project is now a **production-ready, enterprise-grade MLOps pipeline**!
