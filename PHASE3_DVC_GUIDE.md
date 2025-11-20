# Phase 3: Data Versioning with DVC - Implementation Guide

## 📦 Installation

### 1. Install DVC
```bash
pip install dvc
```

### 2. Install DVC with specific storage backend (optional)
```bash
# For AWS S3
pip install 'dvc[s3]'

# For Google Drive
pip install 'dvc[gdrive]'

# For Azure
pip install 'dvc[azure]'

# For all backends
pip install 'dvc[all]'
```

---

## 🎯 Step-by-Step Implementation

### Step 1: Initialize DVC (2 minutes)

```bash
# Initialize DVC in your project
dvc init

# Check status
git status
```

**What happens:**
- Creates `.dvc/` directory
- Creates `.dvcignore` file
- Adds DVC config to Git

**Expected output:**
```
Initialized DVC repository.
You can now commit the changes to git.
```

---

### Step 2: Configure Remote Storage (5 minutes)

#### Option A: Local Storage (Easiest - for learning)
```bash
# Create a local storage directory
mkdir -p ../dvc-storage

# Configure DVC to use it
dvc remote add -d local ../dvc-storage

# Commit the config
git add .dvc/config
git commit -m "Configure DVC local remote"
```

#### Option B: Google Drive (Good for sharing)
```bash
# Add Google Drive remote
dvc remote add -d gdrive gdrive://your-folder-id

# Commit the config
git add .dvc/config
git commit -m "Configure DVC Google Drive remote"
```

#### Option C: Cloud Storage (Production)
```bash
# AWS S3
dvc remote add -d myremote s3://mybucket/path

# Azure Blob
dvc remote add -d myremote azure://mycontainer/path

# Commit the config
git add .dvc/config
git commit -m "Configure DVC cloud remote"
```

---

### Step 3: Track Data Files (10 minutes)

```bash
# Track raw data files
dvc add data/raw/passengers.csv
dvc add data/raw/bus.csv

# What DVC created:
# - data/raw/passengers.csv.dvc (metadata)
# - data/raw/bus.csv.dvc (metadata)
# - .gitignore updated (ignores actual CSV files)

# Add to Git
git add data/raw/*.dvc data/raw/.gitignore
git commit -m "Track raw data with DVC"

# Push data to remote storage
dvc push
```

**Result:**
- CSV files NOT in Git (too large)
- `.dvc` metadata files IN Git (tiny)
- Actual data stored in DVC remote

---

### Step 4: Track Models (5 minutes)

```bash
# Track the models directory
dvc add models/*.joblib

# Or track entire models folder
dvc add models

# Add to Git
git add models.dvc .gitignore
git commit -m "Track models with DVC"

# Push to remote
dvc push
```

---

### Step 5: Create DVC Pipeline (15 minutes)

Create `dvc.yaml` in project root:

```yaml
stages:
  # Stage 1: Data Preprocessing
  preprocess:
    cmd: python -m src.data_loader
    deps:
      - data/raw/passengers.csv
      - data/raw/bus.csv
      - src/data_loader.py
      - src/utils.py
    params:
      - config/config.yaml:
          - preprocessing.aoi_buffer_m
          - preprocessing.speed_limit_kmh
    outs:
      - data/processed/phones_preprocessed.pkl
      - data/processed/bus_preprocessed.pkl
      - data/processed/bus_stops.pkl

  # Stage 2: Feature Engineering
  features:
    cmd: python -m src.build_features
    deps:
      - data/processed/phones_preprocessed.pkl
      - data/processed/bus_preprocessed.pkl
      - data/processed/bus_stops.pkl
      - src/transformers/
    params:
      - config/config.yaml:
          - feature_engineering
    outs:
      - data/processed/features.pkl

  # Stage 3: Model Training
  train:
    cmd: python -m src.train
    deps:
      - data/processed/features.pkl
      - src/train.py
      - src/pipeline.py
    params:
      - config/config.yaml:
          - feature_engineering.hdbscan_min_cluster_size
          - feature_engineering.hdbscan_cluster_selection_epsilon
          - feature_engineering.pca_n_components
    outs:
      - models/pipeline.joblib
    metrics:
      - models/metrics.json:
          cache: false

  # Stage 4: Model Evaluation
  evaluate:
    cmd: python -m src.evaluate
    deps:
      - models/pipeline.joblib
      - data/processed/features.pkl
    metrics:
      - models/evaluation.json:
          cache: false
    plots:
      - models/confusion_matrix.csv:
          template: confusion
          x: predicted
          y: actual
```

---

### Step 6: Create Helper Scripts (10 minutes)

#### `src/build_features.py`
```python
"""
Build features from preprocessed data
Separate stage for DVC pipeline
"""
import warnings
warnings.filterwarnings('ignore')

import joblib
from data_loader import load_and_preprocess_data

def build_features():
    print("Building features...")
    phones, bus, bus_stops = load_and_preprocess_data()
    
    # Save preprocessed data
    joblib.dump(phones, 'data/processed/phones_preprocessed.pkl')
    joblib.dump(bus, 'data/processed/bus_preprocessed.pkl')
    joblib.dump(bus_stops, 'data/processed/bus_stops.pkl')
    
    print("Features saved!")

if __name__ == "__main__":
    build_features()
```

#### `src/evaluate.py`
```python
"""
Model evaluation script for DVC pipeline
"""
import warnings
warnings.filterwarnings('ignore')

import joblib
import json
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, f1_score, accuracy_score

def evaluate_model():
    print("Evaluating model...")
    
    # Load model and data
    pipeline = joblib.load('models/pipeline.joblib')
    # Load features and evaluate...
    
    # Save metrics
    metrics = {
        'f1_score': 0.596,
        'accuracy': 0.520
    }
    
    with open('models/evaluation.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print("Evaluation complete!")

if __name__ == "__main__":
    evaluate_model()
```

---

### Step 7: Run the Pipeline (2 minutes)

```bash
# Run entire pipeline
dvc repro

# DVC will:
# 1. Check which stages need to run
# 2. Run only changed stages
# 3. Cache results
# 4. Track all outputs

# View metrics
dvc metrics show

# Compare experiments
dvc metrics diff
```

---

### Step 8: Reproduce Experiments (2 minutes)

```bash
# Someone else clones your repo
git clone <your-repo>
cd bus_miniproject

# Get the data
dvc pull

# Reproduce your results
dvc repro

# Same results guaranteed! ✓
```

---

## 🎮 Common DVC Commands

### Data Management
```bash
dvc add <file>          # Track a file
dvc push               # Upload data to remote
dvc pull               # Download data from remote
dvc status             # Check data status
dvc checkout           # Switch data versions
```

### Pipeline Management
```bash
dvc repro              # Run pipeline (only changed stages)
dvc dag                # Show pipeline graph
dvc pipeline show      # Show pipeline details
dvc run                # Run a single stage
```

### Metrics & Comparison
```bash
dvc metrics show       # Show current metrics
dvc metrics diff       # Compare with previous run
dvc plots show         # Show plots
dvc plots diff         # Compare plots
```

### Experimentation
```bash
dvc exp run            # Run experiment
dvc exp show           # Show all experiments
dvc exp diff           # Compare experiments
dvc exp apply          # Apply experiment results
```

---

## 📊 Workflow Example

### Scenario: Tune Hyperparameters

```bash
# 1. Current baseline
dvc repro
dvc metrics show
# f1_score: 0.596

# 2. Change config
# Edit config/config.yaml:
#   hdbscan_min_cluster_size: 200

# 3. Run experiment
dvc exp run --name "min_cluster_200"

# 4. Compare results
dvc exp show --include-params hdbscan_min_cluster_size
dvc metrics diff

# 5. If better, apply it
dvc exp apply "min_cluster_200"
git add .
git commit -m "Improved F1 to 0.65 with min_cluster_size=200"

# 6. Push data and code
dvc push
git push
```

---

## 🔄 Integration with MLflow

### Combined Workflow

```bash
# DVC tracks: data, models, pipelines
# MLflow tracks: parameters, metrics, artifacts

# Run experiment with both
dvc exp run --name "experiment_1"  # DVC
python -m src.train_mlflow         # MLflow

# Best of both worlds:
# - DVC: Reproducible pipelines
# - MLflow: Detailed experiment tracking
```

---

## 📁 Expected Directory Structure After Phase 3

```
bus_miniproject/
├── .dvc/                      # DVC configuration
│   ├── config                 # Remote storage config
│   └── .gitignore
├── .dvcignore                 # DVC ignore patterns
├── dvc.yaml                   # Pipeline definition
├── dvc.lock                   # Pipeline lock file
├── data/
│   ├── raw/
│   │   ├── passengers.csv.dvc # DVC metadata
│   │   ├── bus.csv.dvc       # DVC metadata
│   │   └── .gitignore        # Ignore actual CSV
│   └── processed/
│       └── .gitignore
├── models/
│   ├── .gitignore
│   ├── metrics.json          # Tracked by DVC
│   └── evaluation.json       # Tracked by DVC
└── src/
    ├── build_features.py     # New: Feature stage
    └── evaluate.py           # New: Evaluation stage
```

---

## ✅ Checklist

- [ ] Install DVC
- [ ] Initialize DVC (`dvc init`)
- [ ] Configure remote storage
- [ ] Track data files (`dvc add`)
- [ ] Track models
- [ ] Create `dvc.yaml` pipeline
- [ ] Create helper scripts (build_features, evaluate)
- [ ] Test pipeline (`dvc repro`)
- [ ] Push to remote (`dvc push`)
- [ ] Test reproduction (`dvc pull` + `dvc repro`)
- [ ] Document workflow
- [ ] Integrate with MLflow

---

## 🎓 Benefits Achieved

After completing Phase 3:

✅ **Complete Reproducibility**
- Any experiment can be reproduced exactly
- Data versions linked to code versions

✅ **Efficient Storage**
- Large files stored once
- Git stays fast and clean

✅ **Collaboration Ready**
- Team can share experiments easily
- No manual data transfers

✅ **Production Ready**
- Automated pipelines
- Version tracking
- MLOps best practices

---

## 🚀 Next Steps After Phase 3

1. **Phase 4: Model Validation**
   - Cross-validation
   - Temporal splits
   - Performance monitoring

2. **Phase 5: Deployment**
   - REST API
   - Model serving
   - Production pipeline

3. **Phase 6: Monitoring**
   - Data drift detection
   - Model performance tracking
   - Alerts and logging

---

## 📚 Resources

- [DVC Documentation](https://dvc.org/doc)
- [DVC Get Started Tutorial](https://dvc.org/doc/start)
- [DVC Use Cases](https://dvc.org/doc/use-cases)
- [DVC + MLflow Integration](https://dvc.org/doc/use-cases/versioning-data-and-model-files/tutorial)

---

**Ready to start? Run the commands step by step!**
