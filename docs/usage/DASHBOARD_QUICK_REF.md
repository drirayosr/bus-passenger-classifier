# 📊 Phase 6.5 Dashboard - Quick Reference

## 🚀 One-Command Startup

```powershell
# Terminal 1: Start API
python start_api.py

# Terminal 2: Start Dashboard  
python start_dashboard.py
```

Dashboard: http://localhost:8501  
API: http://localhost:8000

---

## 📑 Dashboard Pages Overview

### 🏠 Home
```
┌─────────────────────────────────────────┐
│  🚌 Bus Passenger Classifier Dashboard  │
├─────────────────────────────────────────┤
│  [50,601]     [53,155]      [0.596]     │
│  Passengers   Bus Records   F1 Score    │
├─────────────────────────────────────────┤
│  📋 Project Overview                    │
│  🎯 Model Performance Chart             │
│  📊 Quick Statistics                    │
└─────────────────────────────────────────┘
```

### 📊 Data Explorer
```
┌─────────────────────────────────────────┐
│ [Distributions][Time][User][Raw Data]   │
├─────────────────────────────────────────┤
│  🥧 Label Distribution    📊 Speed      │
│  📈 Acceleration          🚗 Automotive  │
│  🕐 Hourly Activity       📅 Daily       │
│  👥 Top Users             📋 Data Table  │
└─────────────────────────────────────────┘
```

### 🗺️ Map View
```
┌─────────────────────────────────────────┐
│  🗺️ Interactive GPS Map                 │
├─────────────────────────────────────────┤
│    🟢 IN (Green)   🔴 OUT (Red)         │
│                                         │
│    [Sample Size: ━━━━━━○━━ 1000]       │
│                                         │
│  Min Lat: 55.6  Max Lat: 55.9          │
│  Min Lon: 12.4  Max Lon: 12.7          │
└─────────────────────────────────────────┘
```

### 📈 Model Performance
```
┌─────────────────────────────────────────┐
│  [0.520]  [0.596]  [0.523]  [0.522]     │
│  Accuracy  F1      Precision  Recall    │
├─────────────────────────────────────────┤
│  OUT Class          │  IN Class         │
│  ▇▇▇▇▇ 0.53        │  ▇▇▇▇▇ 0.52       │
└─────────────────────────────────────────┘
```

### 🔮 Prediction Tool
```
┌─────────────────────────────────────────┐
│  📍 Enter GPS Data                       │
│  User ID:    [dashboard_test]           │
│  Latitude:   [55.792232]                │
│  Longitude:  [12.522917]                │
│  Timestamp:  [2025-01-20T...]           │
│  Speed:      [0.0] m/s                  │
├─────────────────────────────────────────┤
│  [Station] [Walking] [Moving]           │
│            [🔮 Make Prediction]          │
├─────────────────────────────────────────┤
│  🟢 IN - Passenger Getting On           │
│  Confidence: 0.85                       │
└─────────────────────────────────────────┘
```

### 📡 API Monitor
```
┌─────────────────────────────────────────┐
│  ✅ API Online                           │
│  Model: bus-passenger-classifier v2     │
│  Stage: Production                      │
├─────────────────────────────────────────┤
│  [🔄 Refresh Metrics]                   │
│  predictions_total    1234              │
│  api_calls_total      1500              │
│  errors_total         5                 │
└─────────────────────────────────────────┘
```

---

## 🎯 Common Use Cases

### Use Case 1: Quick Demo
```
1. Home → Show overview
2. Prediction Tool → Click preset → Predict
3. Result: 🟢 IN or 🔴 OUT
```

### Use Case 2: Data Analysis
```
1. Data Explorer → Distributions
2. Time Analysis → Peak hours
3. Map View → Geographic patterns
```

### Use Case 3: Model Evaluation
```
1. Model Performance → Check metrics
2. API Monitor → Verify API status
3. Prediction Tool → Test edge cases
```

### Use Case 4: Presentation
```
1. Home → Project intro
2. Data Explorer → Show data scale
3. Map View → Visual impact
4. Prediction Tool → Live demo
5. Model Performance → Results
```

---

## 🔧 Quick Troubleshooting

### Problem: API Connection Failed
```
✗ Symptom: ❌ API Offline in sidebar
✓ Solution: python start_api.py
✓ Verify:   http://localhost:8000/health
```

### Problem: Dashboard Won't Start
```
✗ Symptom: ModuleNotFoundError: streamlit
✓ Solution: pip install -r requirements-dashboard.txt
✓ Verify:   python -m streamlit --version
```

### Problem: Data Not Loading
```
✗ Symptom: "Unable to load passenger data"
✓ Solution: Ensure passengers.csv in project root
✓ Verify:   dir passengers.csv
```

### Problem: Predictions Fail
```
✗ Symptom: "Model not found" or 400 error
✓ Solution: python src/train_mlflow.py
✓ Verify:   dir models\production_model.pkl
```

---

## 📊 Key Metrics at a Glance

### Data
- **Passengers**: 50,601 records
- **Bus Records**: 53,155 records
- **Unique Users**: Variable (check dashboard)
- **Time Period**: January 2020
- **Location**: Copenhagen (55.6-55.9°N, 12.4-12.7°E)

### Model
- **F1-Score**: 0.596
- **Accuracy**: 52.0%
- **Version**: 2 (Production)
- **Features**: 52
- **Algorithm**: HDBSCAN + PCA

### API
- **Endpoints**: 8 total
- **Port**: 8000
- **Status**: Check /health
- **Docs**: /docs

### Dashboard
- **Pages**: 6 interactive
- **Port**: 8501
- **Charts**: 15+ visualizations
- **Load Time**: < 2 seconds

---

## 🎨 Page Navigation Flow

```
        🏠 Home (Start here)
              │
    ┌─────────┼─────────┬─────────┐
    │         │         │         │
    ▼         ▼         ▼         ▼
  📊 Data  🗺️ Map  📈 Model  🔮 Predict
Explorer   View    Perf     Tool
    │                         │
    │                         ▼
    │                    📡 API Monitor
    │                         │
    └─────────────────────────┘
           (Complete loop)
```

---

## 💡 Pro Tips

### Tip 1: Performance
```
• Reduce map sample size for faster loading
• Clear cache: Press 'C' in dashboard
• Close unused browser tabs
```

### Tip 2: Data Exploration
```
• Start with Time Analysis to find patterns
• Use Raw Data filters to drill down
• Download CSV for offline analysis
```

### Tip 3: Model Testing
```
• Use presets first to understand baseline
• Try edge cases (very fast, very slow)
• Compare different locations
```

### Tip 4: Presentation
```
• Full-screen: F11 in browser
• Hide sidebar: Click arrow in top-left
• Use quick stats on Home for impact
```

### Tip 5: Development
```
• Edit app.py → Save → Auto-refresh
• Check console for errors (F12)
• Test API separately first
```

---

## 📁 Quick File Reference

```
bus_miniproject/
├── start_dashboard.py          ← Launch dashboard
├── dashboard/
│   ├── app.py                  ← Main dashboard code (800+ lines)
│   └── README.md               ← Dashboard-specific docs
├── PHASE6.5_DASHBOARD_SUMMARY.md  ← Full documentation
├── PHASE6.5_COMPLETE.md        ← Completion summary
└── USAGE_GUIDE.md              ← Step-by-step guide
```

---

## 🎯 Decision Tree: What Should I Do?

```
Start Here
│
├─ Want to explore data?
│  └─ Go to: 📊 Data Explorer
│
├─ Need to make predictions?
│  ├─ Is API running?
│  │  ├─ Yes → Go to: 🔮 Prediction Tool
│  │  └─ No → Run: python start_api.py
│  └─ Then → Go to: 🔮 Prediction Tool
│
├─ Want to see performance?
│  └─ Go to: 📈 Model Performance
│
├─ Need to check API?
│  └─ Go to: 📡 API Monitor
│
├─ Want geographic view?
│  └─ Go to: 🗺️ Map View
│
└─ Giving presentation?
   └─ Flow: 🏠 → 📊 → 🗺️ → 📈 → 🔮
```

---

## ⚡ Keyboard Shortcuts

### In Dashboard
- `C` - Clear cache
- `R` - Rerun (refresh)
- `?` - Show shortcuts
- `Ctrl+/` - Focus search

### In Browser
- `F11` - Full screen
- `F12` - Developer tools
- `Ctrl+R` - Refresh page
- `Ctrl+Shift+R` - Hard refresh

---

## 📞 Support Checklist

Before asking for help:
- [ ] Is virtual environment activated?
- [ ] Are dependencies installed?
- [ ] Do data files exist (passengers.csv, bus.csv)?
- [ ] Is API running (check http://localhost:8000/health)?
- [ ] Any errors in terminal console?
- [ ] Any errors in browser console (F12)?
- [ ] Tried restarting dashboard?
- [ ] Checked documentation?

---

## 🎉 Success Indicators

Dashboard is working correctly when you see:

✅ **Sidebar**
- ✅ API Online (green box)
- Model version displayed
- Navigation works

✅ **Home Page**
- Statistics cards show numbers
- Performance chart displays
- No error messages

✅ **Data Explorer**
- Charts render correctly
- Data table shows rows
- Filters work

✅ **Map View**
- Map displays with colored points
- Can zoom and pan
- Statistics show coordinates

✅ **Model Performance**
- Metrics display (accuracy, F1, etc.)
- Charts render
- Configuration shown

✅ **Prediction Tool**
- Form accepts input
- Presets work
- Predictions return results

✅ **API Monitor**
- Health check shows status
- Metrics display
- Endpoints listed

---

**🎨 Dashboard Status: ✅ COMPLETE**

**Ready for: Demos, Presentations, Portfolio Showcase**

**Built with Streamlit | Part of MLOps Pipeline**

---

**Need help? Check:**
- USAGE_GUIDE.md - Step-by-step workflows
- PHASE6.5_DASHBOARD_SUMMARY.md - Full documentation  
- dashboard/README.md - Quick start guide
