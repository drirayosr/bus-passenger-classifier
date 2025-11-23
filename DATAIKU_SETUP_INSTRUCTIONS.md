# Dataiku Setup - Quick Start Guide

## Installation Steps

### 1. Download & Install (5 minutes)
1. Download from: https://www.dataiku.com/product/get-started/
2. Run the installer (.exe file)
3. Installation directory: `C:\Dataiku\dss` (or choose your own)
4. Follow the installation wizard (accept defaults)

### 2. Start Dataiku (1 minute)
After installation, Dataiku should start automatically.

If not, run:
```powershell
# Navigate to Dataiku installation folder
cd C:\Dataiku\dss\bin

# Start Dataiku
.\dss.bat start
```

### 3. Access Dataiku (immediate)
- Open browser: **http://localhost:11200**
- Create your account (local only, no registration)
- You're in!

---

## Import Your Bus Project

### Step 1: Create Project
1. Click **"+ New Project"**
2. Name: `Bus Passenger Classifier`
3. Click **"Create"**

### Step 2: Upload Data
1. Click **"+ Import your first dataset"**
2. Choose **"Upload your files"**
3. Upload `passengers.csv`:
   - Browse to: `C:\Users\FX506\Desktop\Yosr_in_Copenhaguen_25-26\bus_miniproject\passengers.csv`
   - Dataset name: `passengers`
   - Click **"Create"**
4. Repeat for `bus.csv`:
   - Upload: `bus.csv`
   - Dataset name: `buses`

### Step 3: Build Visual Flow

#### Recipe 1: Join Datasets
1. Select `passengers` dataset
2. Click **"Actions"** → **"Join with..."**
3. Choose `buses` dataset
4. Join conditions:
   - Left column: `vehicle_id` = Right column: `vehicle_id`
   - Add second condition: `timestamp_utc` = `utc_time`
5. Join type: **Left join**
6. Output dataset name: `merged_data`
7. Click **"Run"**

#### Recipe 2: Clean Data
1. Select `merged_data`
2. Click **"Lab"** → **"Prepare recipe"**
3. Visual steps (click to add):
   - **"Remove rows"** → Where `vehicle_id` is empty
   - **"Remove rows"** → Where `payload` is empty
   - **"Filter"** → `speed >= 0`
   - **"Filter"** → `payload >= 0`
4. Output dataset: `clean_data`
5. Click **"Run"**

#### Recipe 3: Engineer Features
1. Select `clean_data`
2. Click **"Lab"** → **"Prepare recipe"**
3. Add feature steps:
   - **"Extract from date"** on `timestamp_utc`:
     - Extract: Hour → new column `hour`
     - Extract: Day of week → new column `day_of_week`
     - Extract: Month → new column `month`
   - **"Formula"**: Create `is_weekend` = `day_of_week >= 5`
   - **"Formula"**: Create `is_rush_hour` = `(hour >= 7 && hour <= 9) || (hour >= 16 && hour <= 18)`
   - **"Formula"**: Create `temp_diff` = `inside_temperature - outside_temperature`
4. Output dataset: `features_data`
5. Click **"Run"**

### Step 4: Train Model (AutoML)

1. Select `features_data` dataset
2. Click **"Lab"** → **"AutoML Prediction"**
3. Configuration:
   - **Task**: Multiclass classification
   - **Target variable**: `label` (if you have it, or `payload` for regression)
   - **Features**: Select all engineered features
   - **Train/Test split**: 80/20
   - **Algorithms**: Check all (Random Forest, XGBoost, Logistic Regression)
   - **Metric**: Accuracy (for classification)
4. Click **"Train"**
5. Wait for training (~2-5 minutes)
6. Dataiku shows:
   - Best model
   - Accuracy metrics
   - Feature importance
   - Confusion matrix

### Step 5: Deploy as API

1. Go to trained model
2. Click **"Deploy"**
3. Choose **"API Service"**
4. Settings:
   - Service name: `bus_prediction_api`
   - Endpoint name: `predict`
5. Click **"Deploy"**
6. Test endpoint:
   ```powershell
   curl http://localhost:11200/public/api/v1/<service-id>/predict `
     -H "Content-Type: application/json" `
     -d '{"features": {...}}'
   ```

### Step 6: Create Scenario (Automation)

1. Click **"Scenarios"** (top menu)
2. Click **"+ New Scenario"**
3. Name: `Weekly Model Retraining`
4. Add steps:
   - **Step 1**: Build dataset `merged_data`
   - **Step 2**: Build dataset `clean_data`
   - **Step 3**: Build dataset `features_data`
   - **Step 4**: Retrain model
   - **Step 5**: Deploy to API
5. Add trigger:
   - Type: **Time-based**
   - Frequency: **Weekly**
   - Day: **Sunday**
   - Time: **02:00**
6. Click **"Save"**
7. Click **"Run"** to test

---

## Dataiku UI Overview

```
┌─────────────────────────────────────────┐
│  Dataiku DSS - http://localhost:11200   │
├─────────────────────────────────────────┤
│  Home  Projects  Jobs  Scenarios  ⚙️    │
├─────────────────────────────────────────┤
│                                         │
│  Your Project: Bus Passenger Classifier│
│                                         │
│  📊 Datasets (3)                        │
│    - passengers                         │
│    - buses                              │
│    - merged_data                        │
│                                         │
│  🔧 Recipes (2)                         │
│    - Join recipe                        │
│    - Prepare recipe                     │
│                                         │
│  🤖 Models (1)                          │
│    - bus_classifier                     │
│                                         │
│  🚀 API Services (1)                    │
│    - bus_prediction_api                 │
│                                         │
│  📅 Scenarios (1)                       │
│    - Weekly Model Retraining            │
│                                         │
└─────────────────────────────────────────┘
```

---

## Visual Flow Diagram

After setup, you'll see this in Dataiku:

```
passengers.csv ──┐
                 │
                 ├──► [Join] ──► merged_data ──► [Prepare] ──► clean_data
                 │
buses.csv ───────┘
                                                                    │
                                                                    ▼
                                                            [Prepare/Features]
                                                                    │
                                                                    ▼
                                                              features_data
                                                                    │
                                                                    ▼
                                                               [AutoML]
                                                                    │
                                                                    ▼
                                                            bus_classifier
                                                                    │
                                                                    ▼
                                                              [API Deploy]
                                                                    │
                                                                    ▼
                                                         bus_prediction_api
```

---

## Testing Your Setup

### Test 1: Data Flow
```
Go to Flow view → Click "Run All" → Check green checkmarks
```

### Test 2: Model
```
Go to Model → Performance tab → Check accuracy > 75%
```

### Test 3: API
```powershell
# From PowerShell
curl http://localhost:11200/public/api/v1/services/bus_prediction_api/predict `
  -H "Content-Type: application/json" `
  -d '{"hour": 8, "day_of_week": 1, "speed": 25, "payload": 150}'
```

### Test 4: Scenario
```
Go to Scenarios → Select "Weekly Model Retraining" → Click "Run Now"
```

---

## Troubleshooting

### ❌ Can't access http://localhost:11200
- Check Dataiku is running: `C:\Dataiku\dss\bin\dss.bat status`
- Start if stopped: `C:\Dataiku\dss\bin\dss.bat start`

### ❌ Upload fails
- File size too large? Free edition has limits
- Try with smaller CSV sample first

### ❌ Join recipe fails
- Check column names match exactly
- Verify timestamp formats are compatible

---

## Next Steps

1. ✅ Install Dataiku
2. ✅ Import your CSVs
3. ✅ Build visual flow
4. ✅ Train model with AutoML
5. ✅ Deploy API
6. ✅ Create scenario
7. 🎉 Demo in presentation!

---

## For Your Presentation

Show:
1. **Visual Flow** - Drag-and-drop ML pipeline
2. **AutoML Results** - Model comparison and metrics
3. **API Deployment** - One-click deployment
4. **Scenario** - Automated scheduling

Say:
> "The system integrates with Dataiku DSS for enterprise deployment, providing visual workflow management, AutoML capabilities, and automated retraining through scenarios."
