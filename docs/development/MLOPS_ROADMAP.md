# MLOps Roadmap: Bus Passenger Classification Pipeline

**Project:** Geospatial classification of passengers (IN/OUT of bus)  
**Created:** November 20, 2025  
**Status:** Planning → Implementation

---

## 📋 Executive Summary

### Target State
Production-ready ML system with:
- Parameterized configuration
- Automated training pipeline
- REST API for real-time predictions
- Data validation and monitoring
- CI/CD automation

---

## 🎯 Project Overview

### Problem Statement
Classify whether smartphone users are **inside (1)** or **outside (0)** a bus using GPS trajectories and engineered kinematic features.

### Input Data
1. **`bus.csv`** (~53k rows): Bus GPS traces with vehicle metadata
2. **`passengers.csv`** (~50k rows): Smartphone GPS with ground truth labels

### ML Workflow
1. **Data Loading** → Schema validation, timestamp conversion
2. **Spatial Filtering** → AOI bounding box (50m buffer from bus route)
3. **Feature Engineering:**
   - Kinematic: speed, acceleration, bearing rate variation
   - Proximity: distance to 3 bus stops, distance to 2 buses
4. **Dimensionality Reduction** → PCA (4 components)
5. **Clustering** → HDBSCAN (unsupervised classification)
6. **Evaluation** → F1-score vs ground truth

### Key Dependencies
- pandas, numpy, scikit-learn, hdbscan
- geopy (haversine distance)
- ydata-profiling (EDA)

---

## 🗺️ Implementation Phases

### ✅ Phase 0: Setup & Planning (Current)
- [x] Analyze existing notebook
- [x] Document workflow and architecture
- [ ] Create project structure
- [ ] Setup virtual environment

### 📦 Phase 1: Parameterization & Refactoring (Week 1)
**Goal:** Extract all hardcoded values, create reusable modules

#### Tasks:
- [ ] **1.1** Create `config.yaml` with all parameters:
  - Data paths
  - AOI buffer (50m)
  - Speed limits (35 km/h)
  - PCA components (4)
  - HDBSCAN parameters
  - Bus stop coordinates

- [ ] **1.2** Create project structure:
  ```
  bus_miniproject/
  ├── config/
  │   └── config.yaml
  ├── src/
  │   ├── __init__.py
  │   ├── config.py
  │   ├── data_loader.py
  │   ├── transformers/
  │   │   ├── __init__.py
  │   │   ├── speed.py
  │   │   ├── acceleration.py
  │   │   ├── bearing.py
  │   │   ├── distance_stops.py
  │   │   └── distance_buses.py
  │   ├── pipeline.py
  │   └── utils.py
  ├── data/
  │   ├── raw/
  │   ├── processed/
  │   └── reference/
  ├── models/
  ├── tests/
  ├── requirements.txt
  └── README.md
  ```

- [ ] **1.3** Refactor transformers into modules:
  - Extract `SpeedTransformer` from notebook cell 100
  - Extract `AccelerationTransformer` from cell 102
  - Extract `BearingRateVariationTransformer` from cell 104
  - Extract `DistanceToStopsTransformer` from cell 106
  - Extract `DistanceToBusesTransformer` from cell 108
  - Extract `PcaDBSCANTransformer` from cell 110

- [ ] **1.4** Create utility functions:
  - `haversine_array()` for distance calculation
  - `to_utc()` for timestamp conversion
  - `compute_aoi_bounds()` for spatial filtering
  - `detect_column()` for flexible column detection

- [ ] **1.5** Build main pipeline:
  - Create `build_pipeline()` function
  - Load config dynamically
  - Chain all transformers

**Deliverables:**
- ✅ Modular, reusable codebase
- ✅ Single source of truth for parameters
- ✅ Easier debugging and testing

---

### 🔬 Phase 2: Experiment Tracking (Week 1-2)
**Goal:** Track all experiments, compare models, version artifacts

#### Tasks:
- [ ] **2.1** Setup MLflow:
  ```bash
  pip install mlflow
  mlflow server --host 0.0.0.0 --port 5000
  ```

- [ ] **2.2** Create `src/train.py`:
  - Load data and config
  - Build pipeline
  - Train model
  - Log parameters to MLflow:
    - `aoi_buffer_m`
    - `speed_limit_kmh`
    - `pca_n_components`
    - `hdbscan_min_cluster_size`
  - Log metrics:
    - `f1_weighted`
    - `f1_in_class`
    - `f1_out_class`
  - Log artifacts:
    - Confusion matrix plot
    - Feature importance (PCA explained variance)
  - Register model in MLflow Model Registry

- [ ] **2.3** Compare baseline vs optimized:
  - Run with default parameters
  - Run with tuned HDBSCAN (vary `min_cluster_size`)
  - Run with different PCA components (2, 3, 4, 5)
  - Compare F1-scores in MLflow UI

**Deliverables:**
- ✅ Full experiment history
- ✅ Model versioning
- ✅ Reproducible results

---

### 💾 Phase 3: Data Versioning (Week 2)
**Goal:** Track dataset changes, enable reproducibility

#### Tasks:
- [ ] **3.1** Setup DVC:
  ```bash
  pip install dvc dvc-gdrive
  dvc init
  git add .dvc .dvcignore
  git commit -m "Initialize DVC"
  ```

- [ ] **3.2** Track datasets:
  ```bash
  dvc add data/raw/passengers.csv
  dvc add data/raw/bus.csv
  git add data/raw/.gitignore data/raw/*.dvc
  git commit -m "Track raw data with DVC"
  ```

- [ ] **3.3** Setup remote storage:
  ```bash
  # Option 1: Google Drive
  dvc remote add -d myremote gdrive://<folder-id>
  
  # Option 2: Local network storage
  dvc remote add -d myremote /path/to/shared/storage
  
  dvc push
  ```

- [ ] **3.4** Add data versioning to training:
  - Update `train.py` to run `dvc pull` before training
  - Document data version in MLflow runs

**Deliverables:**
- ✅ Versioned datasets
- ✅ Reproducible data lineage
- ✅ Team collaboration enabled

---

### ✔️ Phase 4: Data Validation (Week 2-3)
**Goal:** Catch data quality issues early

#### Tasks:
- [ ] **4.1** Setup Great Expectations:
  ```bash
  pip install great-expectations
  great_expectations init
  ```

- [ ] **4.2** Create `tests/test_data.py`:
  - Validate `passengers.csv`:
    - Required columns exist
    - Latitude range: [55.79, 55.80]
    - Longitude range: [12.52, 12.53]
    - Speed < 35 km/h
    - No nulls in `user_id`, `timestamp_utc`
    - Timestamp format is UTC
    - `labelEnc2` in {0, 1}
  
  - Validate `bus.csv`:
    - Required columns exist
    - Similar geographic bounds
    - `door_state` in expected values
    - No negative speeds

- [ ] **4.3** Create pytest tests:
  ```bash
  pip install pytest pytest-cov
  ```
  
  Create `tests/test_transformers.py`:
  - Test `SpeedTransformer` output
  - Test `haversine_array()` with known distances
  - Test pipeline end-to-end with small dataset
  - Test edge cases (single user, missing timestamps)

- [ ] **4.4** Add validation to training pipeline:
  - Run Great Expectations before training
  - Fail fast if validation fails
  - Log validation results to MLflow

**Deliverables:**
- ✅ Automated data quality checks
- ✅ Unit tests for all transformers
- ✅ Prevents bad data from training

---

### 📦 Phase 5: Model Packaging (Week 3)
**Goal:** Serialize and version production models

#### Tasks:
- [ ] **5.1** Add model serialization to `train.py`:
  ```python
  import joblib
  from pathlib import Path
  
  # Save pipeline
  model_dir = Path('models')
  model_dir.mkdir(exist_ok=True)
  model_path = model_dir / f'pipeline_v{version}.pkl'
  joblib.dump(pipeline, model_path)
  
  # Also log to MLflow
  mlflow.sklearn.log_model(pipeline, "bus_classifier")
  ```

- [ ] **5.2** Create `src/predict.py`:
  ```python
  def predict(data_path, model_path='models/pipeline.pkl'):
      pipeline = joblib.load(model_path)
      data = pd.read_csv(data_path)
      predictions = pipeline.transform(data)
      return predictions[['user_id', 'pca_dbscan_cluster']]
  ```

- [ ] **5.3** Test model loading:
  - Load saved model
  - Run predictions on test set
  - Verify F1-score matches training

**Deliverables:**
- ✅ Serialized models ready for deployment
- ✅ Inference script for batch predictions
- ✅ Model registry in MLflow

---

### 🚀 Phase 6: API Serving (Week 3-4)
**Goal:** REST API for real-time predictions

#### Tasks:
- [ ] **6.1** Setup FastAPI:
  ```bash
  pip install fastapi uvicorn pydantic
  ```

- [ ] **6.2** Create `api/app.py`:
  - `GET /health` - Health check
  - `POST /predict/batch` - Upload CSV, get predictions
  - `POST /predict/realtime` - Single point prediction
  - Load model at startup (singleton pattern)
  - Add request validation with Pydantic
  - Add error handling

- [ ] **6.3** Create API tests:
  ```bash
  pip install httpx
  ```
  Create `tests/test_api.py`:
  - Test health endpoint
  - Test batch predictions
  - Test realtime predictions
  - Test invalid inputs

- [ ] **6.4** Run API locally:
  ```bash
  uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
  ```

- [ ] **6.5** Create API documentation:
  - Use FastAPI auto-generated docs at `/docs`
  - Add example requests/responses
  - Document rate limits and error codes

**Deliverables:**
- ✅ Production-ready API
- ✅ Interactive documentation
- ✅ Real-time prediction capability

---

### 🔄 Phase 7: CI/CD Pipeline (Week 4)
**Goal:** Automate testing, linting, and deployment

#### Tasks:
- [ ] **7.1** Create `.github/workflows/ci.yml`:
  - Trigger on: push to main, PRs
  - Jobs:
    - Lint with flake8
    - Run pytest with coverage
    - Run data validation
    - Build Docker image (on main only)
    - Push to container registry

- [ ] **7.2** Setup linting:
  ```bash
  pip install flake8 black isort
  ```
  Create `.flake8`:
  ```ini
  [flake8]
  max-line-length = 120
  exclude = .git,__pycache__,venv
  ```

- [ ] **7.3** Create `Dockerfile`:
  ```dockerfile
  FROM python:3.9-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  COPY src/ src/
  COPY api/ api/
  COPY models/ models/
  COPY config/ config/
  EXPOSE 8000
  CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
  ```

- [ ] **7.4** Test Docker locally:
  ```bash
  docker build -t bus-classifier .
  docker run -p 8000:8000 bus-classifier
  ```

- [ ] **7.5** Setup pre-commit hooks:
  ```bash
  pip install pre-commit
  pre-commit install
  ```
  Create `.pre-commit-config.yaml`:
  - Run black (formatting)
  - Run isort (import sorting)
  - Run flake8 (linting)
  - Run pytest (tests)

**Deliverables:**
- ✅ Automated testing on every commit
- ✅ Docker image for deployment
- ✅ Code quality enforcement

---

### ⚙️ Phase 8: Orchestration (Week 5)
**Goal:** Schedule and automate ML workflows

#### Tasks:
- [ ] **8.1** Setup Airflow:
  ```bash
  pip install apache-airflow
  airflow db init
  airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com
  airflow webserver --port 8080 &
  airflow scheduler &
  ```

- [ ] **8.2** Create `airflow/dags/train_pipeline.py`:
  - Task 1: Pull latest data with DVC
  - Task 2: Validate data with Great Expectations
  - Task 3: Train model with MLflow tracking
  - Task 4: Evaluate on validation set
  - Task 5: Deploy if F1 > threshold
  - Schedule: Weekly on Sunday 2 AM
  - Email alerts on failure

- [ ] **8.3** Create `airflow/dags/monitoring.py`:
  - Task 1: Pull production data
  - Task 2: Check for data drift
  - Task 3: Evaluate model performance
  - Task 4: Send alerts if issues detected
  - Schedule: Every 6 hours

- [ ] **8.4** Setup Airflow connections:
  - MLflow connection
  - DVC remote storage
  - Email SMTP settings

**Deliverables:**
- ✅ Automated retraining pipeline
- ✅ Scheduled monitoring
- ✅ Alert system for failures

---

### 📊 Phase 9: Monitoring & Drift Detection (Week 5-6)
**Goal:** Detect data drift and model degradation

#### Tasks:
- [ ] **9.1** Setup Evidently AI:
  ```bash
  pip install evidently
  ```

- [ ] **9.2** Create `src/monitor.py`:
  - Generate drift reports comparing:
    - Reference data (training set)
    - Current production data
  - Monitor features:
    - `speed_mps_computed`
    - `acceleration_mps2_computed`
    - `distance_to_bus_*`
    - `bearing_rate_variation`
  - Check for:
    - Data drift (distribution changes)
    - Data quality issues
    - Missing values increase
    - Outliers

- [ ] **9.3** Create dashboards:
  - HTML reports saved to `reports/`
  - Key metrics:
    - Drift score per feature
    - % of drifted features
    - Data quality metrics
  - Refresh: Every 6 hours via Airflow

- [ ] **9.4** Add alerting:
  - Send Slack/email if drift detected
  - Trigger retraining if drift > threshold
  - Log all alerts to MLflow

- [ ] **9.5** Create `api/app.py` monitoring endpoint:
  - `POST /monitor/drift` - Check uploaded data for drift
  - Return drift report summary

**Deliverables:**
- ✅ Drift detection system
- ✅ Automated alerts
- ✅ Dashboard for monitoring

---

### 📈 Phase 10: Performance Monitoring (Week 6)
**Goal:** Track API performance and model quality in production

#### Tasks:
- [ ] **10.1** Add Prometheus metrics to API:
  ```bash
  pip install prometheus-client
  ```
  
  Track:
  - Total predictions made
  - Prediction latency (p50, p95, p99)
  - Error rate
  - Predictions per class (IN/OUT)

- [ ] **10.2** Setup Prometheus:
  ```bash
  docker run -p 9090:9090 -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus
  ```

- [ ] **10.3** Setup Grafana:
  ```bash
  docker run -p 3000:3000 grafana/grafana
  ```
  
  Create dashboards:
  - Prediction throughput
  - Latency percentiles
  - Error rates
  - Class distribution over time

- [ ] **10.4** Add logging:
  ```python
  import logging
  logging.basicConfig(level=logging.INFO)
  logger = logging.getLogger(__name__)
  
  # Log all predictions with timestamps
  logger.info(f"Prediction: user={user_id}, class={pred}, latency={latency}")
  ```

- [ ] **10.5** Setup log aggregation:
  - Collect logs to file
  - Rotate logs daily
  - Parse for patterns (errors, slow predictions)

**Deliverables:**
- ✅ Real-time performance monitoring
- ✅ Grafana dashboards
- ✅ Structured logging

---

## 📁 Final Project Structure

```
bus_miniproject/
├── .github/
│   └── workflows/
│       └── ci.yml                 # CI/CD pipeline
├── airflow/
│   └── dags/
│       ├── train_pipeline.py      # Training orchestration
│       └── monitoring.py          # Monitoring orchestration
├── api/
│   ├── __init__.py
│   └── app.py                     # FastAPI application
├── config/
│   └── config.yaml                # All parameters
├── data/
│   ├── raw/                       # Original CSVs (DVC tracked)
│   │   ├── bus.csv
│   │   ├── passengers.csv
│   │   ├── .gitignore
│   │   ├── bus.csv.dvc
│   │   └── passengers.csv.dvc
│   ├── processed/                 # After AOI filtering
│   └── reference/                 # Baseline for drift detection
├── models/
│   ├── pipeline.pkl               # Trained model
│   └── metadata.json              # Model version info
├── reports/
│   └── drift_reports/             # Evidently HTML reports
├── src/
│   ├── __init__.py
│   ├── config.py                  # Config loader
│   ├── data_loader.py             # Data loading utilities
│   ├── train.py                   # Training script
│   ├── predict.py                 # Inference script
│   ├── monitor.py                 # Drift monitoring
│   ├── pipeline.py                # Main pipeline builder
│   ├── utils.py                   # Helper functions
│   └── transformers/
│       ├── __init__.py
│       ├── speed.py               # SpeedTransformer
│       ├── acceleration.py        # AccelerationTransformer
│       ├── bearing.py             # BearingRateVariationTransformer
│       ├── distance_stops.py      # DistanceToStopsTransformer
│       ├── distance_buses.py      # DistanceToBusesTransformer
│       └── pca_dbscan.py          # PcaDBSCANTransformer
├── tests/
│   ├── __init__.py
│   ├── test_data.py               # Great Expectations suites
│   ├── test_transformers.py       # Unit tests
│   ├── test_pipeline.py           # Integration tests
│   └── test_api.py                # API tests
├── notebooks/
│   └── AAU_Worshop_whosOnBus.ipynb  # Original research notebook
├── .dvc/                          # DVC configuration
├── .gitignore
├── .flake8                        # Linting config
├── .pre-commit-config.yaml        # Pre-commit hooks
├── Dockerfile                     # Container definition
├── docker-compose.yml             # Multi-container orchestration
├── requirements.txt               # Python dependencies
├── setup.py                       # Package installation
├── MLOPS_ROADMAP.md              # This document
└── README.md                      # Project documentation
```

---

## 🛠️ Technology Stack

| Component | Tool | Purpose |
|-----------|------|---------|
| **Config** | YAML | Externalize parameters |
| **Pipeline** | sklearn Pipeline | Reproducible ML workflow |
| **Experiment Tracking** | MLflow | Track runs, metrics, models |
| **Data Versioning** | DVC | Version datasets |
| **Data Validation** | Great Expectations | Schema/quality checks |
| **Testing** | pytest | Unit/integration tests |
| **Packaging** | joblib | Serialize models |
| **API** | FastAPI | REST endpoints |
| **CI/CD** | GitHub Actions | Automated workflows |
| **Orchestration** | Apache Airflow | Schedule jobs |
| **Drift Detection** | Evidently AI | Monitor data/model drift |
| **Metrics** | Prometheus | API performance |
| **Visualization** | Grafana | Dashboards |
| **Containerization** | Docker | Deployment |
| **Linting** | flake8, black | Code quality |

---

## 📊 Success Metrics

### Technical KPIs
- ✅ **F1-Score**: Maintain ≥70% on validation set
- ✅ **API Latency**: p95 < 200ms
- ✅ **Test Coverage**: ≥80%
- ✅ **Drift Detection**: Catch within 6 hours
- ✅ **Uptime**: ≥99.5%

### Process KPIs
- ✅ **Experiment Tracking**: 100% of runs logged
- ✅ **Code Quality**: All PRs pass linting
- ✅ **Deployment Time**: < 10 minutes from commit to production
- ✅ **Monitoring**: Real-time dashboards operational

---

## 🚦 Getting Started

### Prerequisites
```bash
# Python 3.9+
python --version

# Git
git --version

# Docker (optional)
docker --version
```

### Quick Start
```bash
# 1. Clone repository
cd c:\..\bus_miniproject

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell

# 3. Install dependencies (to be created)
pip install -r requirements.txt

# 4. Run training script (to be created)
python src/train.py

# 5. Start API (to be created)
uvicorn api.app:app --reload
```

---

## 📝 Next Steps

**Immediate Actions (This Session):**
1. ✅ Create this roadmap document
2. ⏳ Create project structure (folders)
3. ⏳ Create `requirements.txt`
4. ⏳ Create `config/config.yaml`
5. ⏳ Extract first transformer (`SpeedTransformer`)

**Priority for Next Session:**
- Complete Phase 1 (Parameterization)
- Setup MLflow (Phase 2)
- Create basic training script

---

## 🤝 Contributing

This is a learning project. Key principles:
- **Incremental**: Implement one phase at a time
- **Test-driven**: Write tests before implementation
- **Document**: Comment complex logic
- **Version control**: Commit frequently with clear messages

---

## 📚 Resources

### Documentation
- [MLflow Docs](https://mlflow.org/docs/latest/index.html)
- [DVC Docs](https://dvc.org/doc)
- [Great Expectations](https://docs.greatexpectations.io/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Evidently AI](https://docs.evidentlyai.com/)

### Tutorials
- [MLOps Best Practices](https://ml-ops.org/)
- [Made With ML](https://madewithml.com/)

---

**Last Updated:** November 20, 2025  
**Version:** 1.0  
**Status:** Ready to implement 🚀
