# Installation Guide

## Quick Start (PowerShell)

### Step 1: Create Virtual Environment
```powershell
cd c:\Users\FX506\Desktop\Yosr_in_Copenhaguen_25-26\bus_miniproject
python -m venv venv
```

### Step 2: Activate Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

**If you get an error about execution policy:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Upgrade pip
```powershell
python -m pip install --upgrade pip
```

### Step 4: Install Dependencies

**Option A: Production setup (recommended)**
```powershell
pip install -r requirements.txt
```
This installs everything needed for production: base ML pipeline, MLflow tracking, and REST API.

**Option B: Install only what you need**
```powershell
# Core ML pipeline only
pip install -r requirements/base.txt

# Development environment (includes testing & code quality tools)
pip install -r requirements/dev.txt

# Dashboard only
pip install -r requirements/dashboard.txt
```

**Option C: Custom setup**
```powershell
# Base + MLflow + API (production)
pip install -r requirements/prod.txt

# Base + specific components
pip install -r requirements/base.txt
pip install -r requirements/mlflow.txt  # Adds MLflow tracking
pip install -r requirements/api.txt     # Adds FastAPI
```

See [requirements/README.md](../../requirements/README.md) for full documentation.

### Step 5: Test Installation
```powershell
python src/config.py
python src/utils.py
```

---

## Optional: Install Additional Components

### Install MLflow (for experiment tracking)
```powershell
pip install -r requirements/mlflow.txt
```

### Install FastAPI (for API serving)
```powershell
pip install -r requirements/api.txt
```

### Install Testing Tools
```powershell
pip install -r requirements/test.txt
```

---

## Troubleshooting

### Issue: "cannot be loaded because running scripts is disabled"
**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: "No module named 'sklearn'"
**Solution:**
```powershell
pip install scikit-learn
```

### Issue: HDBSCAN installation fails
**Solution (requires Visual Studio Build Tools):**
1. Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Install "Desktop development with C++"
3. Restart terminal
4. Try again: `pip install hdbscan`

**Alternative (pre-built wheels):**
```powershell
pip install hdbscan --only-binary :all:
```

### Issue: Other package conflicts
**Solution:** Install one by one
```powershell
pip install pandas
pip install numpy
pip install scikit-learn
pip install hdbscan
pip install geopy
pip install matplotlib
pip install seaborn
pip install pyyaml
pip install joblib
```

---

## Verify Installation

```powershell
# Check Python version
python --version

# Check installed packages
pip list

# Test imports
python -c "import pandas; import numpy; import sklearn; print('All good!')"
```

---

## What's Installed?

### Core Requirements (requirements-core.txt)
- **pandas**: Data manipulation
- **numpy**: Numerical operations
- **scikit-learn**: Machine learning pipeline
- **hdbscan**: Clustering algorithm
- **geopy**: Geospatial distance calculations
- **matplotlib & seaborn**: Plotting
- **pyyaml**: Configuration files
- **joblib**: Model serialization

### MLflow (requirements-mlflow.txt)
- Experiment tracking
- Model registry
- Metrics logging

### FastAPI (requirements-api.txt)
- REST API framework
- API documentation
- Request validation

### Testing (requirements-test.txt)
- pytest: Test framework
- pytest-cov: Coverage reports
- httpx: API testing

---

## Next Steps

After successful installation:

1. **Move data files**:
   ```powershell
   # Copy bus.csv and passengers.csv to data/raw/
   ```

2. **Test transformers**:
   ```powershell
   python src/transformers/speed.py
   ```

3. **Ready to build the pipeline!**
