# Phase 5: Model Registry - Implementation Guide

## Overview
Phase 5 implements MLflow Model Registry for production-grade model versioning, staging, and deployment management.

## What Was Implemented

### 1. Core Components

```
src/
├── model_registry.py      # Model Registry class and CLI
├── registry_manager.py    # Interactive management tool
└── predict.py            # Inference with registry models
```

### 2. ModelRegistry Class

**Key Features:**
- Register models from MLflow runs
- Version management (automatic versioning)
- Stage transitions (None → Staging → Production)
- Model retrieval by version or stage
- Model metadata and description management

**Methods:**
```python
class ModelRegistry:
    def register_model(run_id, model_name)
    def get_latest_run(experiment_name)
    def promote_model(model_name, version, stage)
    def get_model_by_stage(model_name, stage)
    def list_registered_models()
    def get_model_info(model_name, version)
    def add_description(model_name, version, description)
```

## How to Use

### Step 1: Train Model with MLflow

```bash
# Train and log to MLflow
python -m src.train_mlflow
```

This creates:
- Experiment: `bus_passenger_classification`
- Run with logged parameters, metrics, and model artifact

### Step 2: Register the Model

**Option A: Register latest model**
```bash
python -m src.model_registry --register
```

**Option B: Register specific run**
```python
from src.model_registry import ModelRegistry

registry = ModelRegistry()
registry.register_model(
    run_id="<run_id>",
    model_name="bus-passenger-classifier"
)
```

### Step 3: Promote Model Through Stages

```bash
# Promote to Staging for testing
python registry_manager.py --promote 1 --stage Staging

# After validation, promote to Production
python registry_manager.py --promote 1 --stage Production
```

**Stages explained:**
- **None**: Newly registered, not deployed anywhere
- **Staging**: Under testing, not customer-facing
- **Production**: Live, serving real traffic
- **Archived**: Deprecated, kept for history

### Step 4: Use Model for Predictions

```python
from src.predict import load_model_from_registry, predict

# Load production model
model = load_model_from_registry(
    model_name="bus-passenger-classifier",
    stage="Production"
)

# Make predictions
passenger_data = {
    'user_id': [1, 1, 1],
    'timestamp_utc': [...],
    'latitude': [55.80, 55.801, 55.802],
    'longitude': [12.52, 12.521, 12.522]
}

predictions = predict(model, passenger_data)
```

## Model Lifecycle Workflow

### Development → Staging → Production

```
1. TRAIN
   └─> MLflow Run Created
       └─> Metrics logged (F1, Accuracy)
       └─> Model artifact saved

2. REGISTER
   └─> Model Version 1 created
       └─> Stage: None
       └─> Metadata: Training date, metrics

3. VALIDATE (Staging)
   └─> Promote to Staging
       └─> Run integration tests
       └─> Test on held-out data
       └─> Monitor performance

4. DEPLOY (Production)
   └─> Promote to Production
       └─> Serve real traffic
       └─> Monitor in production
       └─> A/B test if needed

5. RETIRE
   └─> Archive old version
       └─> Keep for reproducibility
```

## Command Reference

### Register Model
```bash
# Register latest training run
python -m src.model_registry --register

# Interactive model browser
python -m src.model_registry
```

### Manage Models
```bash
# List all registered models
python registry_manager.py --list

# Get model info
python registry_manager.py --info bus-passenger-classifier --version 1

# Promote model
python registry_manager.py --promote 1 --stage Production

# Add description
python registry_manager.py --describe 1 --description "Optimized HDBSCAN with epsilon=0.5"

# Compare versions
python registry_manager.py --compare 1 2
```

### Make Predictions
```bash
# Predict with production model
python -m src.predict --stage Production --input data/test_sample.csv

# Predict with specific version
python -m src.predict --version 2 --input data/test_sample.csv
```

## MLflow UI Integration

### Start MLflow UI
```bash
python start_mlflow_ui.py
```

Then navigate to: http://localhost:5000

### UI Features
1. **Experiments Tab**: View all training runs
2. **Models Tab**: Browse registered models
   - See all versions
   - Compare metrics across versions
   - Manage stages
   - View lineage (which run produced this model)

### Model Details Page
- **Overview**: Version, stage, creation date
- **Source Run**: Link to original training run
- **Metrics**: F1, accuracy, confusion matrix
- **Artifacts**: Model file, plots
- **Activities**: Stage transitions, description updates

## Benefits of Model Registry

### 1. **Version Control for Models**
- Every model is versioned automatically
- Track which code/data produced each model
- Reproduce any model version

### 2. **Stage Management**
- Clear separation: Development vs Staging vs Production
- Gradual rollout with validation gates
- Easy rollback if issues found

### 3. **Model Lineage**
- Know which training run produced a model
- Track hyperparameters that created it
- Link to data version (via DVC)

### 4. **Collaboration**
- Team can see what's in production
- Clear ownership and approval workflow
- Audit trail of all changes

### 5. **Deployment Integration**
- APIs can load "production" model dynamically
- No hard-coded model paths
- Zero-downtime model updates

## Example Workflow

### Scenario: Improving the Model

```bash
# 1. Experiment with new hyperparameters
# Edit config.yaml: min_cluster_size = 500
python -m src.train_mlflow

# 2. Compare results in MLflow UI
# F1 improved from 0.596 to 0.650!

# 3. Register new model
python -m src.model_registry --register
# Created version 2

# 4. Deploy to staging for testing
python registry_manager.py --promote 2 --stage Staging

# 5. Run validation tests
python -m src.predict --stage Staging --input data/validation.csv
# Looks good!

# 6. Promote to production
python registry_manager.py --promote 2 --stage Production

# 7. Archive old model
python registry_manager.py --promote 1 --stage Archived
```

## Integration with Other Phases

### Phase 2 (MLflow Tracking)
- Registry builds on tracked experiments
- Models come from logged runs
- Metrics inform promotion decisions

### Phase 3 (DVC)
- Model version links to data version
- Reproducible: DVC hash + Model version
- Can recreate any model from scratch

### Phase 4 (Validation)
- Run data validation before registering
- Include test results in model metadata
- Validation must pass for Staging promotion

### Phase 6 (REST API) - Next
- API loads model from registry
- `GET /model/info` → Returns current production version
- `POST /predict` → Uses production model
- Hot reload when model updated

## Model Metadata Best Practices

### Add Rich Descriptions
```python
registry.add_description(
    model_name="bus-passenger-classifier",
    version=2,
    description="""
    HDBSCAN optimization with epsilon=0.5
    - F1: 0.650 (+0.054 vs baseline)
    - Trained on 2025-01-20 data
    - AOI buffer: 50m
    - Features: speed, acceleration, bearing, distances, PCA
    - Validated on held-out set: 95% of staging predictions match labels
    """
)
```

### Tag Models
```python
mlflow.set_tag("validation_status", "passed")
mlflow.set_tag("data_version", "dvc:a3f45bc")
mlflow.set_tag("approved_by", "data-science-team")
```

## Troubleshooting

### "Experiment not found"
**Problem**: No MLflow experiments exist yet

**Solution**:
```bash
python -m src.train_mlflow
```

### "No runs found"
**Problem**: Experiment exists but no successful runs

**Solution**: Check MLflow UI for failed runs, fix training script

### "Model already registered"
**Problem**: Trying to register same run twice

**Solution**: This is OK! MLflow will return existing version

### "Backend store not found"
**Problem**: MLflow tracking URI not set

**Solution**: Ensure `mlruns/` directory exists or set:
```python
mlflow.set_tracking_uri("sqlite:///mlflow.db")  # For SQLite backend
```

## Advanced Features

### A/B Testing Setup
```python
# Deploy two models to production
registry.promote_model("bus-passenger-classifier", version=1, stage="Production")
registry.promote_model("bus-passenger-classifier", version=2, stage="Production")

# In API, split traffic:
if random.random() < 0.5:
    model = load_model_from_registry(model_name, version=1)
else:
    model = load_model_from_registry(model_name, version=2)
```

### Model Comparison
```bash
python registry_manager.py --compare 1 2

Output:
Version 1:
  F1: 0.596
  Accuracy: 0.520
  Stage: Archived
  
Version 2:
  F1: 0.650 (+9.1%)
  Accuracy: 0.580 (+11.5%)
  Stage: Production
```

### Automated Promotion (CI/CD)
```python
# In CI pipeline
if f1_score > 0.60 and accuracy > 0.55:
    registry.promote_model(model_name, version, "Staging")
    
    # Run integration tests
    test_results = run_integration_tests()
    
    if test_results.passed:
        registry.promote_model(model_name, version, "Production")
```

## Files Created

1. **src/model_registry.py** - Core registry functionality
2. **registry_manager.py** - CLI management tool
3. **src/predict.py** - Inference with registry models
4. **test_registry.py** - Registry functionality tests
5. **PHASE5_REGISTRY_GUIDE.md** - This document

## Next Steps

Phase 5 is now **READY TO USE** once you have MLflow runs!

**To complete Phase 5:**

1. ✅ Run training with MLflow:
   ```bash
   python -m src.train_mlflow
   ```

2. ✅ Register the model:
   ```bash
   python -m src.model_registry --register
   ```

3. ✅ View in MLflow UI:
   ```bash
   python start_mlflow_ui.py
   # Open http://localhost:5000
   ```

4. ✅ Promote to production:
   ```bash
   python registry_manager.py --promote 1 --stage Production
   ```

**Next Phase Options:**

- **Phase 6: REST API** - Deploy as FastAPI service
- **Phase 7: CI/CD** - Automate testing and deployment
- **Phase 8: Monitoring** - Track production performance

What would you like to do next?
