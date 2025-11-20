# Requirements Structure

This folder contains organized requirements files for different use cases.

## Files Overview

- **`base.txt`** - Core ML pipeline dependencies (pandas, scikit-learn, hdbscan, geopy)
- **`mlflow.txt`** - MLflow for experiment tracking and model registry
- **`api.txt`** - FastAPI REST API dependencies
- **`dashboard.txt`** - Streamlit interactive dashboard
- **`test.txt`** - Testing framework (pytest)
- **`dev.txt`** - Development tools (linting, formatting, jupyter)
- **`prod.txt`** - Production environment (base + mlflow + api)

## Quick Start

```bash
# For basic ML pipeline only
pip install -r requirements/base.txt

# For production (API + MLflow + base)
pip install -r requirements/prod.txt

# For development (includes testing & code quality)
pip install -r requirements/dev.txt

# Or use the main requirements.txt (defaults to prod)
pip install -r requirements.txt
```

## Docker

The Dockerfile uses these organized requirements:
```dockerfile
COPY requirements/base.txt requirements/mlflow.txt requirements/api.txt ./
RUN pip install -r base.txt && \
    pip install -r mlflow.txt && \
    pip install -r api.txt
```

## Dependency Chain

```
base.txt
├── mlflow.txt (base + mlflow)
├── api.txt (base + fastapi)
├── dashboard.txt (base + streamlit)
├── test.txt (base + pytest)
└── dev.txt (base + test + code quality tools)
    
prod.txt = base + mlflow + api
```
