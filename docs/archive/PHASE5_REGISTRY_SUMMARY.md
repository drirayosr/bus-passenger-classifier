# Phase 5: Model Registry - Complete ✅

## Overview
Successfully implemented MLflow Model Registry for production-grade model versioning and lifecycle management.

## What Was Implemented

### 1. Model Registry System (`src/model_registry.py`)
Complete model lifecycle management with MLflow:

**Key Features:**
- ✅ Register models from training runs
- ✅ Version management (automatic versioning)
- ✅ Stage promotion (None → Staging → Production → Archived)
- ✅ Model comparison between versions
- ✅ Load production models programmatically
- ✅ List all registered models

**Core Methods:**
```python
registry = ModelRegistry()
registry.register_model(run_id, model_name)
registry.promote_model(model_name, version, stage)
registry.load_production_model(model_name)
registry.compare_models(model_name, version1, version2)
```

### 2. CLI Management Tool (`registry_manager.py`)
Command-line interface for all registry operations:

```bash
# Register latest model
python registry_manager.py register

# List all models
python registry_manager.py list

# Get model info
python registry_manager.py info --name bus-passenger-classifier --stage Production

# Promote model
python registry_manager.py promote --version 2 --stage Production

# Compare versions
python registry_manager.py compare --v1 1 --v2 2
```

### 3. Inference Script (`src/predict.py`)
Production-ready prediction script:

**Features:**
- ✅ Load models from registry (by stage or version)
- ✅ Batch predictions on datasets
- ✅ Confidence scores (using PCA distance)
- ✅ Prediction summaries and statistics
- ✅ Save predictions to CSV

**Usage:**
```bash
# Use production model
python -m src.predict

# Use staging model
python -m src.predict --stage Staging

# Custom input file
python -m src.predict --input data/test.csv --output predictions/out.csv
```

### 4. Setup Script (`setup_registry.py`)
Quick setup and status checker for the model registry.

## Current Production Model

**Status:** ✅ READY

```
Model: bus-passenger-classifier
  Version: 2
  Stage: Production
  Status: READY
  Run ID: 559c789d2f874acdae972090bdff437d
  Performance: F1 = 0.596, Accuracy = 52.0%
```

## Model Lifecycle Workflow

```
1. Train Model
   ↓
   python -m src.train_mlflow
   
2. Register Model
   ↓
   python registry_manager.py register
   (Creates Version 1, Stage: None)
   
3. Promote to Staging
   ↓
   python registry_manager.py promote --version 1 --stage Staging
   
4. Validate in Staging
   ↓
   python -m src.predict --stage Staging
   
5. Promote to Production
   ↓
   python registry_manager.py promote --version 1 --stage Production
   
6. Use in Production
   ↓
   python -m src.predict
   (Automatically loads Production model)
```

## Key Benefits Achieved

### 1. **Version Control for Models**
- Every model is versioned automatically
- Track which model version is in which stage
- Easy rollback if needed

### 2. **Stage-Based Deployment**
- Clear separation: None → Staging → Production
- Test in Staging before Production
- Archive old models

### 3. **Model Lineage**
- Link models to training runs
- See exact parameters and metrics
- Reproducible deployments

### 4. **Production Safety**
- Only one Production model at a time
- Automatic archiving of old Production models
- Clear audit trail of promotions

### 5. **Easy Model Loading**
```python
# Load production model
model = registry.load_production_model()

# Or by version
model = mlflow.sklearn.load_model("models:/bus-passenger-classifier/2")

# Or by stage
model = mlflow.sklearn.load_model("models:/bus-passenger-classifier/Production")
```

## Integration Points

### With Phase 2 (MLflow Tracking)
- Models registered from tracked experiments
- Metrics and parameters linked to versions
- Run IDs connect training to deployment

### With Phase 3 (DVC)
- Data versions tracked separately
- Model versions track which data was used
- Complete reproducibility

### With Phase 4 (Validation)
- Validate data before training
- Validate staging model before production
- Quality gates at every stage

## Common Operations

### Compare Two Model Versions
```bash
python registry_manager.py compare --v1 1 --v2 2
```

Output:
```
Comparing bus-passenger-classifier v1 vs v2
============================================================

Version 1 (Stage: Archived):
  accuracy            : 0.5100
  f1_score            : 0.5900
  
Version 2 (Stage: Production):
  accuracy            : 0.5200
  f1_score            : 0.5960

Comparison:
  f1_score            : 0.5900 vs 0.5960 (↑ 0.0060)
  accuracy            : 0.5100 vs 0.5200 (↑ 0.0100)
```

### List All Models and Versions
```bash
python registry_manager.py list
```

### Rollback to Previous Version
```bash
# Archive current production
python registry_manager.py promote --version 2 --stage Archived

# Promote old version
python registry_manager.py promote --version 1 --stage Production
```

### Load Model in Python
```python
from src.model_registry import ModelRegistry

registry = ModelRegistry()
model = registry.load_production_model()

# Make predictions
predictions = model.transform(data)
```

## Model Registry Structure in MLflow

```
MLflow Tracking Server
├── Experiments
│   └── bus-passenger-classification
│       ├── Run 1 (F1=0.590)
│       ├── Run 2 (F1=0.596) ← Registered
│       └── Run 3 (F1=0.585)
│
└── Model Registry
    └── bus-passenger-classifier
        ├── Version 1
        │   ├── Stage: Archived
        │   ├── Run ID: abc123...
        │   └── Metrics: F1=0.590
        │
        └── Version 2 ← Production
            ├── Stage: Production
            ├── Run ID: 559c789d...
            └── Metrics: F1=0.596
```

## Files Created

1. **src/model_registry.py** - Model registry Python API
2. **registry_manager.py** - CLI tool for registry management
3. **src/predict.py** - Inference script with registry integration
4. **setup_registry.py** - Setup and status checker
5. **PHASE5_REGISTRY_SUMMARY.md** - This documentation

## Testing the System

### Test 1: Register Model
```bash
python registry_manager.py register
```
✅ Expected: Model registered with version number

### Test 2: Promote to Staging
```bash
python registry_manager.py promote --version 2 --stage Staging
```
✅ Expected: Model moved to Staging stage

### Test 3: Load and Predict
```bash
python -m src.predict --stage Staging
```
✅ Expected: Predictions generated successfully

### Test 4: Promote to Production
```bash
python registry_manager.py promote --version 2 --stage Production
```
✅ Expected: Model in Production, old Production archived

## Next Steps Options

**Phase 5 Complete!** ✅ You now have:
- Versioned models in MLflow
- Stage-based deployment (Staging/Production)
- Production model ready for inference

**Choose your next phase:**

### Option 1: Phase 6 - REST API Deployment
Deploy your model as a REST API:
- FastAPI service
- Docker containerization
- Swagger documentation
- Real-time predictions

### Option 2: Phase 7 - CI/CD Pipeline
Automate the entire workflow:
- GitHub Actions
- Automated testing
- Automated model deployment
- Continuous training

### Option 3: Stop and Document
You've built a solid MLOps foundation:
- ✅ Modular code (Phase 1)
- ✅ Experiment tracking (Phase 2)
- ✅ Data versioning (Phase 3)
- ✅ Data validation (Phase 4)
- ✅ Model registry (Phase 5)

This is production-ready for batch processing!

## What You Can Do Now

### Batch Predictions
```bash
python -m src.predict
```

### Train New Model
```bash
python -m src.train_mlflow
python registry_manager.py register
python registry_manager.py promote --version 3 --stage Production
```

### Monitor in MLflow UI
```bash
python start_mlflow_ui.py
# Open http://localhost:5000
# Navigate to "Models" tab
```

### Deploy with Docker (Future)
```dockerfile
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
CMD ["python", "-m", "src.predict"]
```

---

**Phase 5 Status: ✅ COMPLETE**

**Production Model:** `bus-passenger-classifier` v2 is live and ready for inference!
