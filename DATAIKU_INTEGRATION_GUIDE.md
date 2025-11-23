# Dataiku Integration Guide

This guide explains how to integrate your Bus Passenger Classifier project with Dataiku DSS (Data Science Studio).

## What is Dataiku?

**Dataiku DSS** is an enterprise data science platform that provides:
- 🎨 **Visual Flow Builder** - Drag-and-drop ML pipelines
- 🔄 **ETL & Data Prep** - No-code data processing
- 🤖 **AutoML** - Automated model selection
- 📊 **Collaboration** - Team workspace for data scientists
- 🚀 **Deployment** - One-click model deployment
- 📈 **Monitoring** - Built-in model performance tracking

---

## Dataiku vs Your Current Stack

| Component | Your Current Stack | Dataiku Equivalent |
|-----------|-------------------|-------------------|
| Data Processing | Python scripts | Visual recipes |
| Feature Engineering | Custom code | Prepare recipe |
| Model Training | scikit-learn | Visual ML |
| MLflow | Model tracking | Model registry |
| Prefect | Orchestration | Scenarios |
| FastAPI | Serving | API deployer |
| Streamlit | Dashboard | Dashboards |

---

## Integration Architecture

```
┌─────────────────────────────────────────────────┐
│           Dataiku DSS Platform                  │
│                                                 │
│  ┌──────────────┐  ┌──────────────┐           │
│  │   Data       │  │   Visual     │           │
│  │   Sources    │──│   Flow       │           │
│  └──────────────┘  └──────────────┘           │
│         │                  │                    │
│         ▼                  ▼                    │
│  ┌──────────────┐  ┌──────────────┐           │
│  │   Prepare    │  │   Feature    │           │
│  │   Recipe     │──│   Engineering│           │
│  └──────────────┘  └──────────────┘           │
│         │                  │                    │
│         ▼                  ▼                    │
│  ┌──────────────┐  ┌──────────────┐           │
│  │   AutoML     │  │   Model      │           │
│  │   Training   │──│   Evaluation │           │
│  └──────────────┘  └──────────────┘           │
│         │                  │                    │
│         ▼                  ▼                    │
│  ┌──────────────────────────────────┐         │
│  │     API Deployer / Scenarios      │         │
│  └──────────────────────────────────┘         │
└─────────────────────────────────────────────────┘
         │                  │
         ▼                  ▼
┌────────────────┐  ┌────────────────┐
│   Your FastAPI │  │   Streamlit    │
│   (External)   │  │   Dashboard    │
└────────────────┘  └────────────────┘
```

---

## Option 1: Dataiku Free Edition (Local)

### Installation

1. **Download Dataiku DSS Free Edition**
   - Go to: https://www.dataiku.com/product/get-started/
   - Click "Free Edition"
   - Download for Windows

2. **Install**
   - Run installer
   - Choose installation directory
   - Start Dataiku server

3. **Access UI**
   - Open browser: http://localhost:11200
   - Create account (local only)

---

## Option 2: Import Your Project into Dataiku

### Step 1: Create Dataiku Project

1. In Dataiku UI, click **"+ New Project"**
2. Name: `Bus Passenger Classifier`
3. Click **"Create"**

### Step 2: Import CSV Data

1. Click **"+ Import your first dataset"**
2. Upload `passengers.csv` → Dataset name: `passengers`
3. Repeat for `bus.csv` → Dataset name: `buses`

### Step 3: Create Visual Flow

#### Recipe 1: Join Data
1. Click **"+ New Recipe"** → **"Join"**
2. Select `passengers` and `buses`
3. Join on: `vehicle_id` and `timestamp`
4. Output dataset: `merged_data`

#### Recipe 2: Prepare Data
1. Select `merged_data` → **"+ New Recipe"** → **"Prepare"**
2. Visual steps:
   - Remove missing values
   - Parse timestamps
   - Create time features (hour, day_of_week)
   - Filter outliers
3. Output dataset: `clean_data`

#### Recipe 3: Train Model
1. Select `clean_data` → **"Lab"** → **"AutoML Prediction"**
2. Settings:
   - Target: `label` (passenger count category)
   - Features: Select all relevant columns
   - Algorithm: Random Forest, XGBoost
3. Train and evaluate

### Step 4: Deploy Model as API

1. Go to trained model → **"Deploy"**
2. Choose **"Real-time API"**
3. Dataiku creates REST API endpoint
4. Test with: `curl http://localhost:11200/api/...`

### Step 5: Create Scenario (Automation)

1. Click **"Scenarios"** → **"+ New Scenario"**
2. Add steps:
   - **Step 1**: Build dataset `merged_data`
   - **Step 2**: Build dataset `clean_data`
   - **Step 3**: Retrain model
   - **Step 4**: Deploy to API
3. Add trigger:
   - **Schedule**: Weekly on Sundays
   - **Time**: 2:00 AM

---

## Option 3: Use Dataiku Cloud

### Sign Up (Free Trial)

1. Go to: https://www.dataiku.com/product/online/
2. Start free trial (14 days)
3. No credit card required

### Connect to Your Data

1. Create new project
2. Add connection:
   - **Type**: File upload or Cloud storage
   - Upload your CSV files

### Follow Flow Creation Steps (Same as above)

---

## Migrating Your Code to Dataiku

### Your Python Code → Dataiku Recipes

#### Current: `src/data_processing.py`
```python
def load_and_process_data(passengers_df, bus_df):
    # Merge data
    df = pd.merge(passengers_df, bus_df, on='vehicle_id')
    # Clean data
    df = df.dropna()
    return df
```

**Dataiku Equivalent:**
- **Join Recipe**: Merge passengers + buses
- **Prepare Recipe**: Remove missing values (visual)

---

#### Current: `src/feature_engineering.py`
```python
def engineer_features(df):
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    return df
```

**Dataiku Equivalent:**
- **Prepare Recipe** → Add steps:
  - Extract from date: Hour
  - Extract from date: Day of week

---

#### Current: `src/model_training.py`
```python
model = RandomForestClassifier()
model.fit(X_train, y_train)
```

**Dataiku Equivalent:**
- **AutoML Prediction** → Select Random Forest
- Dataiku trains, tunes, and evaluates automatically

---

## Dataiku Scenarios vs Prefect

### Your Prefect Workflow:
```python
@flow(name="Training Pipeline")
def training_pipeline():
    load_data()
    process_data()
    train_model()
    save_model()
```

### Dataiku Scenario Equivalent:

1. **Create Scenario** → Name: "Weekly Training"
2. **Add Steps**:
   - Build dataset: `merged_data`
   - Build dataset: `clean_data`
   - Retrain model: `classifier_model`
   - Deploy: `API Endpoint`
3. **Add Trigger**:
   - Type: Time-based
   - Schedule: Weekly
   - Run on: Sunday 2:00 AM

**Result**: Same automation, no code required!

---

## Dataiku API Deployer vs FastAPI

### Your FastAPI:
```python
@app.post("/predict")
def predict(data: PassengerData):
    model = joblib.load("models/pipeline.joblib")
    prediction = model.predict(data)
    return {"prediction": prediction}
```

### Dataiku API Deployer:

1. Select trained model
2. Click **"Deploy"** → **"API Service"**
3. Dataiku generates endpoint automatically
4. Test with:
   ```bash
   curl -X POST http://dataiku:11200/api/v1/model/predict \
     -H "Content-Type: application/json" \
     -d '{"features": [...]}'
   ```

**Result**: API without writing code!

---

## Hybrid Approach (Recommended)

### Use Both Dataiku + Your Stack

```
┌─────────────────────────────────────┐
│         Dataiku DSS                 │
│  - Visual data prep                 │
│  - AutoML experimentation          │
│  - Business user collaboration     │
└────────────┬────────────────────────┘
             │
             │ Export Model
             ▼
┌─────────────────────────────────────┐
│      Your Production Stack          │
│  - FastAPI (custom logic)          │
│  - MLflow (version control)        │
│  - Streamlit (custom dashboard)    │
└─────────────────────────────────────┘
```

### Export Model from Dataiku

1. Train model in Dataiku
2. Export as Python code or pickle
3. Load in your FastAPI:
   ```python
   model = joblib.load("dataiku_model.pkl")
   ```

---

## Dataiku Dashboards vs Streamlit

### Your Streamlit Dashboard:
- Custom Python code
- Full control
- Requires coding

### Dataiku Dashboards:
- Drag-and-drop widgets
- No code required
- Built-in charts

**Use Case:**
- **Dataiku Dashboard**: For business users
- **Streamlit**: For technical users / custom features

---

## Cost Comparison

| Edition | Price | Features |
|---------|-------|----------|
| **Free Edition** | $0 | Single user, local only, full features |
| **Dataiku Cloud Trial** | $0 (14 days) | Cloud-hosted, team collaboration |
| **Team** | ~$5,000/year | 3 users, cloud or on-prem |
| **Enterprise** | Custom | Unlimited users, advanced features |

**For your project**: Use **Free Edition** (perfect for demos!)

---

## Step-by-Step: Add Dataiku to Your Project

### 1. Install Dataiku Free Edition

```powershell
# Download from: https://www.dataiku.com/product/get-started/
# Run installer
# Start Dataiku server
```

### 2. Create Project Structure File

I'll create a Dataiku project export configuration:

---

## Benefits for Your Presentation

✅ **Visual Workflows** - Show drag-and-drop ML pipeline
✅ **AutoML** - Demonstrate automated model selection
✅ **No-Code** - Business users can modify pipelines
✅ **Enterprise-Ready** - Used by Fortune 500 companies
✅ **Collaboration** - Team can work together in same platform

---

## Demo Flow for Presentation

1. **Show Visual Flow**
   - Drag datasets
   - Connect recipes
   - Build pipeline visually

2. **Show AutoML Training**
   - Click "Train"
   - Dataiku tries multiple algorithms
   - Shows best model automatically

3. **Show Deployment**
   - One-click deploy to API
   - Instant REST endpoint

4. **Show Scenario**
   - Scheduled retraining
   - Automatic deployment
   - No code required

---

## Integration with Azure ML

Since you mentioned Azure ML, here's the connection:

### Dataiku + Azure ML

1. **In Dataiku**:
   - Create Azure ML connection
   - Train model in Dataiku
   - Export to Azure ML workspace

2. **Azure ML receives**:
   - Trained model
   - Training code
   - Deployment config

3. **Azure ML handles**:
   - Scalable inference
   - Model monitoring
   - Production deployment

**Command in Dataiku**:
```python
# In Dataiku Python recipe
from dataiku import pandasutils as pdu
from azureml.core import Workspace, Model

# Train model in Dataiku
model = train_model(dataset)

# Register in Azure ML
ws = Workspace.from_config()
Model.register(workspace=ws, model_path="model.pkl")
```

---

## Your Complete Stack with Dataiku

```
┌─────────────────────────────────────────────┐
│              Dataiku DSS                    │
│  Visual ML | AutoML | Collaboration        │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
┌──────────────┐     ┌──────────────┐
│   MLflow     │     │  Azure ML    │
│ (Tracking)   │     │ (Production) │
└──────────────┘     └──────────────┘
        │                     │
        └──────────┬──────────┘
                   ▼
        ┌──────────────────────┐
        │      FastAPI         │
        │   (Serving Layer)    │
        └──────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │   Streamlit          │
        │   (Dashboard)        │
        └──────────────────────┘
```

---

## Next Steps

1. ✅ **Download Dataiku Free**: https://www.dataiku.com/product/get-started/
2. ✅ **Import your CSVs**: passengers.csv, bus.csv
3. ✅ **Build visual flow**: Join → Prepare → Train → Deploy
4. ✅ **Create scenario**: Schedule weekly retraining
5. 🎯 **Demo in presentation**: Show visual ML pipeline!

---

## Quick Start Commands

```powershell
# Install Dataiku (after download)
# Windows: Run DSS installer

# Start Dataiku
dataiku-dss start

# Open UI
# Browser: http://localhost:11200

# Stop Dataiku
dataiku-dss stop
```

---

**Dataiku adds enterprise-grade ML platform to your project! 🚀**

For your presentation, you can say:
> "The system is designed for enterprise deployment with Dataiku DSS integration, enabling visual workflow design, AutoML capabilities, and no-code model deployment for business users."
