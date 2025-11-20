# 🚀 Complete Usage Guide - Bus Passenger Classifier

**Step-by-step guide to using all components of the MLOps pipeline**

---

## 📋 Table of Contents

1. [Initial Setup](#initial-setup)
2. [Training a Model](#training-a-model)
3. [Using the REST API](#using-the-rest-api)
4. [Exploring with Dashboard](#exploring-with-dashboard)
5. [Running Tests](#running-tests)
6. [Common Workflows](#common-workflows)
7. [Troubleshooting](#troubleshooting)

---

## 🔧 Initial Setup

### Step 1: Environment Setup

```powershell
# Navigate to project directory
cd c:\Users\FX506\Desktop\Yosr_in_Copenhaguen_25-26\bus_miniproject

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Verify Python version (should be 3.9+)
python --version
```

### Step 2: Install Dependencies

**Option A: Install all at once**
```powershell
pip install -r requirements-core.txt
pip install -r requirements-mlflow.txt
pip install -r requirements-api.txt
pip install -r requirements-dashboard.txt
pip install -r requirements-test.txt
```

**Option B: Install as needed**
```powershell
# Core ML (always required)
pip install -r requirements-core.txt

# Add MLflow for training
pip install -r requirements-mlflow.txt

# Add API for serving
pip install -r requirements-api.txt

# Add dashboard for visualization
pip install -r requirements-dashboard.txt

# Add testing tools
pip install -r requirements-test.txt
```

### Step 3: Verify Data Files

```powershell
# Check if data files exist
dir passengers.csv
dir bus.csv

# Output should show:
# passengers.csv (~62 MB, 50,601 rows)
# bus.csv (~60 MB, 53,155 rows)
```

---

## 🎓 Training a Model

### Basic Training

```powershell
# Train model with default config
python src/train_mlflow.py

# Expected output:
# ✅ Data loaded: 50,601 records
# 🔬 Training with HDBSCAN(min_cluster_size=300, epsilon=0.5)
# 📊 F1-Score: 0.596
# ✅ Model saved: models/production_model.pkl
```

### View Results in MLflow UI

```powershell
# Terminal 1: Start MLflow UI
mlflow ui --host 127.0.0.1 --port 5000

# Open browser: http://localhost:5000
# You'll see:
# - All experiments
# - Model parameters (PCA components, HDBSCAN settings)
# - Metrics (F1, accuracy, precision, recall)
# - Artifacts (model files, charts)
```

### Training with Custom Config

```powershell
# Edit config/config.yaml first, then run:
python src/train_mlflow.py

# Example changes in config.yaml:
# feature_engineering:
#   pca_n_components: 6           # Try more PCA components
#   hdbscan_min_cluster_size: 500  # Larger cluster size
```

### Registering Models

```powershell
# Models are automatically registered to MLflow Model Registry
# View in MLflow UI: http://localhost:5000/#/models

# Promote model to Production:
# 1. Go to MLflow UI
# 2. Click "Models" tab
# 3. Select "bus-passenger-classifier"
# 4. Click version number
# 5. Click "Stage: None" → "Transition to → Production"
```

---

## 🚀 Using the REST API

### Starting the API

```powershell
# Terminal 1: Start API
python start_api.py

# Expected output:
# INFO: Loading model from MLflow Model Registry...
# INFO: Model loaded: bus-passenger-classifier version 2 (Production)
# INFO: Uvicorn running on http://0.0.0.0:8000
```

### Testing Endpoints

**Health Check**
```powershell
# Using curl (if available)
curl http://localhost:8000/health

# Using Python
python -c "import requests; print(requests.get('http://localhost:8000/health').json())"

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2025-01-20T10:00:00.000000",
#   "model_loaded": true,
#   "model_info": {
#     "model_name": "bus-passenger-classifier",
#     "version": "2",
#     "stage": "Production"
#   }
# }
```

**Single Prediction**
```powershell
# Run the example client
python api_client_examples.py

# Or manually with Python:
python
>>> import requests
>>> payload = {
...     "id": "test_user",
...     "lat": 55.792232,
...     "lon": 12.522917,
...     "timestamp_utc": "2020-01-22T10:16:22.321000+00:00",
...     "speed": 0.0
... }
>>> response = requests.post("http://localhost:8000/predict/single", json=payload)
>>> print(response.json())
{
  "predicted_label": 1,  # 1 = IN, 0 = OUT
  "confidence": 0.85,
  "user_id": "test_user",
  "model_info": {...}
}
```

**Batch Prediction**
```python
import requests

payload = {
    "data": [
        {
            "id": "user1",
            "lat": 55.792232,
            "lon": 12.522917,
            "timestamp_utc": "2020-01-22T10:16:22.321000+00:00",
            "speed": 0.0
        },
        {
            "id": "user2",
            "lat": 55.792244,
            "lon": 12.522932,
            "timestamp_utc": "2020-01-22T10:16:32.321000+00:00",
            "speed": 1.5
        }
    ]
}

response = requests.post("http://localhost:8000/predict/batch", json=payload)
print(response.json())
# Returns list of predictions
```

**CSV Upload**
```python
import requests

# Upload CSV file for predictions
with open('test_data.csv', 'rb') as f:
    files = {'file': ('test_data.csv', f, 'text/csv')}
    response = requests.post("http://localhost:8000/predict/csv", files=files)
    print(response.json())
```

### Viewing API Documentation

```powershell
# Open in browser:
start http://localhost:8000/docs

# Interactive API documentation (Swagger UI)
# - Try all endpoints
# - See request/response schemas
# - Test with example values
```

---

## 🎨 Exploring with Dashboard

### Starting the Dashboard

```powershell
# Terminal 1: Start API (required for predictions)
python start_api.py

# Terminal 2: Start Dashboard
python start_dashboard.py

# Dashboard opens automatically at: http://localhost:8501
```

### Dashboard Tour

#### 🏠 Home Page
**What you'll see:**
- Total passengers: 50,601
- Bus records: 53,155
- Model F1 score: 0.596
- Quick statistics (IN/OUT records, unique users, avg speed)
- Model performance bar chart

**What to do:**
- Get overview of project
- Check model metrics
- Understand dataset size

#### 📊 Data Explorer
**What you'll see:**
- **Distributions Tab**: Label pie chart, speed histogram, acceleration distribution
- **Time Analysis Tab**: Activity by hour/day charts
- **User Analysis Tab**: Top 20 users, user statistics
- **Raw Data Tab**: Filterable table, CSV download

**What to do:**
1. Explore label distribution (IN vs OUT balance)
2. Check time patterns (peak hours, busy days)
3. View user activity levels
4. Filter and download data samples

**Example workflow:**
```
1. Go to Data Explorer
2. Click "Time Analysis" tab
3. Observe peak activity around 8-9 AM and 5-6 PM
4. Switch to "User Analysis"
5. See most active users (top 20)
6. Go to "Raw Data" tab
7. Filter by label: select "IN"
8. Download first 100 rows
```

#### 🗺️ Map View
**What you'll see:**
- Interactive scatter mapbox of GPS points
- Color-coded: Green (IN) vs Red (OUT)
- Geographic statistics (min/max lat/lon)

**What to do:**
1. Adjust sample size slider (start with 1000)
2. Zoom and pan to explore Copenhagen area
3. Identify hotspots and patterns
4. Check coordinate ranges

**Tips:**
- Lower sample size for faster rendering
- Green clusters = bus stops/stations (passengers getting on)
- Red clusters = destinations (passengers getting off)

#### 📈 Model Performance
**What you'll see:**
- Key metrics: Accuracy, F1-score, Precision, Recall
- Class-specific performance (IN vs OUT)
- Model configuration details

**What to do:**
- Compare IN vs OUT performance
- Identify which class is harder to predict
- Review model configuration

**Interpretation:**
- F1-score ~0.596 = decent but room for improvement
- Check if one class has much lower performance
- Compare precision vs recall trade-offs

#### 🔮 Prediction Tool
**What you'll see:**
- Manual input form (User ID, lat, lon, timestamp, speed)
- Quick test presets (Station Stop, Walking, Moving)
- Real-time prediction results (🟢 IN / 🔴 OUT)
- Confidence scores

**What to do:**
1. **Quick Test**: Click "Preset 1: Station Stop" → "Make Prediction"
2. **Custom Test**: Enter your own coordinates → "Make Prediction"
3. **Compare**: Try all 3 presets to see different predictions

**Example workflow:**
```
1. Click "Preset 1: Station Stop"
   → Result: 🟢 IN (confidence: 0.85)
   → Interpretation: Stationary at station = likely boarding

2. Click "Preset 3: Moving"
   → Result: 🔴 OUT (confidence: 0.72)
   → Interpretation: Moving away = likely already off bus

3. Custom test: Enter Copenhagen coordinates
   - Lat: 55.676098 (City Hall)
   - Lon: 12.568337
   - Speed: 0.0
   → See if it predicts IN (popular stop)
```

#### 📡 API Monitor
**What you'll see:**
- API health status (✅ green = online)
- Model information (version, stage)
- Prometheus metrics (prediction counts, errors)
- Endpoint documentation

**What to do:**
1. Verify API is online
2. Check model version in production
3. Refresh metrics to see API activity
4. Review available endpoints

**Metrics explanation:**
- `predictions_total`: Total predictions made
- `api_calls_total`: Total API requests
- `errors_total`: Failed requests (should be low)

---

## ✅ Running Tests

### Data Validation Tests

```powershell
# Run all data validation tests
pytest tests/test_data_validation.py -v

# Expected output:
# tests/test_data_validation.py::test_passengers_file_exists PASSED
# tests/test_data_validation.py::test_passengers_not_empty PASSED
# ... (19 tests total)
# ==================== 19 passed in 2.45s ====================

# Run specific test
pytest tests/test_data_validation.py::test_no_missing_coordinates -v

# Run with coverage
pytest tests/test_data_validation.py --cov=src --cov-report=html
# Opens htmlcov/index.html for detailed coverage report
```

### Test Categories

**File Existence Tests:**
- `test_passengers_file_exists`
- `test_bus_file_exists`

**Data Integrity Tests:**
- `test_passengers_not_empty`
- `test_bus_not_empty`
- `test_required_columns_passengers`
- `test_required_columns_bus`

**Data Quality Tests:**
- `test_no_missing_coordinates`
- `test_coordinates_valid_range`
- `test_timestamps_valid`
- `test_speed_reasonable`
- `test_no_duplicate_timestamps_per_user`

**Statistical Tests:**
- `test_label_distribution`
- `test_speed_distribution`

---

## 🔄 Common Workflows

### Workflow 1: First-Time User
```powershell
# 1. Setup
.\venv\Scripts\Activate.ps1
pip install -r requirements-core.txt

# 2. Train model
python src/train_mlflow.py

# 3. Check results
mlflow ui

# 4. Explore data
pip install -r requirements-dashboard.txt
python start_dashboard.py
# → Go to Data Explorer and Map View

# 5. Test predictions
pip install -r requirements-api.txt
python start_api.py
# → Use Prediction Tool in dashboard
```

### Workflow 2: Experimenting with Hyperparameters
```powershell
# 1. Edit config/config.yaml
# Change: pca_n_components from 4 to 6

# 2. Train with new config
python src/train_mlflow.py

# 3. Compare in MLflow UI
mlflow ui
# → Click "Compare" button
# → Select both runs
# → See side-by-side metrics

# 4. Test new model via API
python start_api.py  # Loads latest Production model
python api_client_examples.py
```

### Workflow 3: Deploying Updated Model
```powershell
# 1. Train improved model
python src/train_mlflow.py

# 2. Register in MLflow
# → Open MLflow UI: http://localhost:5000
# → Go to Models → bus-passenger-classifier
# → Click new version
# → Transition to Production

# 3. Restart API to load new model
# Ctrl+C to stop API
python start_api.py
# → Check /health endpoint shows new version

# 4. Verify in dashboard
# → Refresh API Monitor page
# → Check "Model Information" shows new version
```

### Workflow 4: Analyzing Model Performance
```powershell
# 1. Run tests to validate data quality
pytest tests/test_data_validation.py -v

# 2. Train model and save metrics
python src/train_mlflow.py

# 3. Review metrics in dashboard
python start_dashboard.py
# → Go to Model Performance page
# → Check F1-score, accuracy, precision, recall
# → Compare IN vs OUT class performance

# 4. Analyze errors
# → Go to Data Explorer
# → Filter by specific labels
# → Look for patterns in misclassified data
```

### Workflow 5: Presenting to Stakeholders
```powershell
# 1. Ensure API is running
python start_api.py

# 2. Start dashboard
python start_dashboard.py

# 3. Presentation flow:
# → Home: Project overview, quick stats
# → Data Explorer: Show data patterns, time analysis
# → Map View: Geographic distribution, hotspots
# → Model Performance: Metrics, class performance
# → Prediction Tool: Live demo with presets
# → API Monitor: Show production-ready API

# 4. Interactive demo:
# → Click "Preset 1" → Show IN prediction
# → Click "Preset 3" → Show OUT prediction
# → Explain confidence scores
```

---

## 🐛 Troubleshooting

### API Won't Start

**Error: "Address already in use"**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID with actual number)
taskkill /PID <PID> /F

# Restart API
python start_api.py
```

**Error: "Model not found"**
```powershell
# Train a model first
python src/train_mlflow.py

# Verify model exists
dir models\production_model.pkl

# Or check MLflow Registry
mlflow ui
# → Go to Models tab
```

### Dashboard Won't Start

**Error: "Module not found: streamlit"**
```powershell
# Install dashboard dependencies
pip install -r requirements-dashboard.txt

# Verify installation
python -m streamlit --version
```

**Error: "Cannot load passengers.csv"**
```powershell
# Check if file exists
dir passengers.csv

# Verify you're in project root
cd c:\Users\FX506\Desktop\Yosr_in_Copenhaguen_25-26\bus_miniproject
```

### Predictions Fail

**Error: "Feature names should match"**
```powershell
# This means model was trained with different features
# Solution: Retrain model with current data
python src/train_mlflow.py

# Restart API
python start_api.py
```

**Error: "Invalid coordinates"**
```
# Coordinates must be in valid ranges:
# Latitude: -90 to 90
# Longitude: -180 to 180
# Copenhagen area: lat ~55.6-55.9, lon ~12.4-12.7
```

### Tests Fail

**Error: "CSV file not found"**
```powershell
# Ensure data files are in project root
dir passengers.csv bus.csv

# If missing, copy from backup or re-download
```

**Error: "AssertionError in test_coordinates_valid_range"**
```
# Data has coordinates outside Copenhagen
# This is expected - tests are validating data quality
# Review which rows are out of range:
python -c "import pandas as pd; df = pd.read_csv('passengers.csv'); print(df[(df['lat'] < 55.6) | (df['lat'] > 55.9)])"
```

### Performance Issues

**Dashboard is slow**
```
# Solutions:
# 1. Reduce sample size in Map View (slider)
# 2. Clear Streamlit cache (press 'C' in dashboard)
# 3. Close unused browser tabs
# 4. Restart dashboard
```

**Training takes too long**
```powershell
# Reduce data size for testing
# Edit src/train_mlflow.py:
# Add: df = df.sample(10000)  # Use 10K samples

# Or reduce HDBSCAN min_cluster_size in config.yaml
```

---

## 🎯 Next Steps

### For Learning
1. **Understand the code**: Read through transformers in `src/transformers/`
2. **Experiment**: Change config parameters and retrain
3. **Explore MLflow**: Compare multiple experiment runs
4. **Customize dashboard**: Add new charts or tabs

### For Production
1. **Add authentication**: Secure API endpoints
2. **Deploy to cloud**: Use Docker for containerization
3. **Setup monitoring**: Track model drift
4. **Implement CI/CD**: Automate testing and deployment

### For Portfolio
1. **Document findings**: Create presentation slides
2. **Add visualizations**: Export charts from dashboard
3. **Write blog post**: Explain methodology and results
4. **Share on GitHub**: Make repository public with good README

---

## 📚 Additional Resources

- **MLflow Documentation**: https://mlflow.org/docs/latest/index.html
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Streamlit Documentation**: https://docs.streamlit.io/
- **HDBSCAN Tutorial**: https://hdbscan.readthedocs.io/
- **Project Roadmap**: See `MLOPS_ROADMAP.md`
- **API Details**: See `PHASE6_API_SUMMARY.md`
- **Dashboard Details**: See `PHASE6.5_DASHBOARD_SUMMARY.md`

---

## ✨ Tips & Best Practices

1. **Always activate virtual environment** before running commands
2. **Use MLflow UI** to track all experiments
3. **Test API** with `/health` endpoint before making predictions
4. **Start small**: Use data samples for quick iterations
5. **Document changes**: Update config.yaml and commit to git
6. **Monitor metrics**: Regularly check API Monitor in dashboard
7. **Version models**: Use MLflow Registry to manage versions
8. **Backup data**: Keep copies of CSV files
9. **Review logs**: Check console output for errors
10. **Ask for help**: Check documentation or error messages

---

**Happy MLOps! 🚀**
