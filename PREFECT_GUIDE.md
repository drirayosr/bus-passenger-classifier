# 🔄 Prefect Orchestration - Quick Start Guide

## What is Prefect?

Prefect automates your ML workflows - training, predictions, and monitoring run on schedules automatically.

## Setup (2 minutes)

### 1. Install Prefect
```powershell
pip install -r requirements/orchestration.txt
```

### 2. Start Prefect Server
Open a NEW terminal:
```powershell
prefect server start
```

The UI will open at: **http://localhost:4200**

---

## Your Workflows

### 📅 Automated Schedules

| Workflow | Schedule | Purpose |
|----------|----------|---------|
| **weekly-model-training** | Sunday 2 AM | Retrain model weekly |
| **daily-batch-predictions** | Daily 8 AM | Run predictions daily |
| **model-monitoring** | Every 6 hours | Check for drift |

### 🎯 What Each Workflow Does

#### 1. Training Flow (`train_model_flow`)
```
Load Data → Validate → Train Model → Get Metrics
```
- Loads `passengers.csv` and `bus.csv`
- Validates data quality
- Triggers training via API
- Fetches metrics from MLflow

#### 2. Predictions Flow (`batch_predictions_flow`)
```
Check Health → Load Data → Make Predictions
```
- Checks API is running
- Loads latest data
- Makes sample predictions

#### 3. Monitoring Flow (`model_monitoring_flow`)
```
Check Health → Get Metrics → Detect Drift → Auto-Retrain if needed
```
- Monitors model performance
- Detects if accuracy drops below 75%
- **Automatically triggers retraining if drift detected**

---

## Usage

### Option A: Automatic Scheduling

1. **Deploy workflows** (one time):
```powershell
python deploy_workflows.py
```

2. **Start Prefect server**:
```powershell
prefect server start
```

3. **Done!** Workflows run automatically on schedule

### Option B: Manual Execution

Run workflows manually anytime:

```powershell
# Train model
python workflows.py train

# Run predictions
python workflows.py predict

# Check monitoring
python workflows.py monitor
```

---

## Prefect UI (http://localhost:4200)

### Dashboard View
```
┌─────────────────────────────────────────┐
│  Prefect UI - http://localhost:4200     │
├─────────────────────────────────────────┤
│  📊 Flows                                │
│    - train_model         [Active]       │
│    - batch_predictions   [Active]       │
│    - model_monitoring    [Active]       │
│                                         │
│  📅 Deployments                         │
│    - weekly-model-training              │
│      Next: Sunday 2:00 AM               │
│    - daily-batch-predictions            │
│      Next: Tomorrow 8:00 AM             │
│    - model-monitoring                   │
│      Next: In 6 hours                   │
│                                         │
│  📈 Flow Runs (Recent)                  │
│    - train_model_flow    ✅ Completed   │
│    - monitoring_flow     ✅ Completed   │
│    - predictions_flow    ✅ Completed   │
└─────────────────────────────────────────┘
```

### What You Can See:
- ✅ Flow execution history
- ⏱️ Execution duration
- 📊 Success/failure rates
- 🔄 Scheduled runs
- 📝 Detailed logs for each run

---

## Integration with Your Stack

### Current Setup
```
Your Services:
├── FastAPI (port 8000)     ← Prefect calls this for training/predictions
├── MLflow (port 5000)      ← Prefect reads metrics from here
├── Streamlit (port 8501)   ← Manual dashboard (unchanged)
└── Prefect (port 4200)     ← NEW: Automation layer
```

### How It Works
```
┌──────────────┐
│   Prefect    │  Orchestrates everything
│  Workflows   │
└──────┬───────┘
       │
       ├─────► [FastAPI] POST /train
       │         └─► Trains model
       │
       ├─────► [FastAPI] POST /predict
       │         └─► Makes predictions
       │
       └─────► [MLflow] GET metrics
                 └─► Monitors performance
```

---

## Quick Test

### 1. Start All Services

**Terminal 1** - FastAPI:
```powershell
python start_api.py
```

**Terminal 2** - MLflow:
```powershell
python start_mlflow_ui.py
```

**Terminal 3** - Prefect:
```powershell
prefect server start
```

### 2. Run a Test Flow

**Terminal 4**:
```powershell
python workflows.py train
```

You should see:
```
=== Starting Model Training Flow ===
Loading data from CSV files...
Loaded 1000 passenger records
Loaded 500 bus records
Validating data...
Triggering model training...
Training completed successfully!
=== Model Training Flow Completed ===
```

### 3. Check Prefect UI

Open **http://localhost:4200** and see your flow run! 🎉

---

## Benefits vs Dataiku

| Feature | Prefect | Dataiku |
|---------|---------|---------|
| **Setup Time** | 2 minutes | 30+ minutes |
| **Code-Based** | ✅ Python | ⚠️ Visual + Python |
| **Lightweight** | ✅ Yes | ❌ Heavy |
| **Learning Curve** | Easy | Steep |
| **Good For** | Developers | Data teams |

---

## Workflow Files

```
bus_miniproject/
├── workflows.py              # ← Workflow definitions
├── deploy_workflows.py       # ← Deployment script
└── requirements/
    └── orchestration.txt     # ← Prefect dependency
```

---

## Troubleshooting

### ❌ "Connection refused" when running workflow
**Fix**: Make sure FastAPI is running on port 8000
```powershell
python start_api.py
```

### ❌ Can't access Prefect UI
**Fix**: Start Prefect server
```powershell
prefect server start
```

### ❌ Workflows don't run automatically
**Fix**: Deploy workflows first
```powershell
python deploy_workflows.py
```

---

## For Your Presentation

### Show This:
1. **Prefect UI** - Visual flow runs and schedules
2. **Code** - Simple Python workflows (workflows.py)
3. **Automatic retraining** - Drift detection triggers training

### Say This:
> "The system uses Prefect for workflow orchestration, automating model training, predictions, and monitoring. When drift is detected, it automatically triggers retraining without manual intervention."

---

## Next Steps

1. ✅ Install: `pip install -r requirements/orchestration.txt`
2. ✅ Start Prefect: `prefect server start`
3. ✅ Deploy workflows: `python deploy_workflows.py`
4. ✅ Test manually: `python workflows.py train`
5. 🎉 Watch it run automatically!

**Ready to go!** 🚀
