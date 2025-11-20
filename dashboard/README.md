# 🚌 Bus Passenger Classifier Dashboard

Interactive Streamlit dashboard for exploring bus passenger data and testing ML predictions in real-time.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r ../requirements-dashboard.txt
```

### 2. Start the Dashboard
```bash
# From project root
python start_dashboard.py

# Or directly
streamlit run dashboard/app.py
```

### 3. Open Browser
The dashboard will automatically open at: http://localhost:8501

## 📊 Features

### 🏠 Home
- Project overview and statistics
- Model performance summary
- Dataset metrics

### 📊 Data Explorer
- Distribution analysis (labels, speed, sensors)
- Time-based patterns (hourly, daily)
- User analysis
- Raw data viewer with filters

### 🗺️ Map View
- Interactive GPS visualization
- Color-coded by prediction (IN/OUT)
- Geographic statistics

### 📈 Model Performance
- Accuracy, F1-score, precision, recall
- Class-specific metrics
- Model configuration

### 🔮 Prediction Tool
- Manual GPS input form
- Quick test presets
- Real-time API predictions
- Visual results (🟢 IN / 🔴 OUT)

### 📡 API Monitor
- API health check
- Model information
- Prometheus metrics
- Endpoint documentation

## ⚙️ Configuration

### API URL
Default: `http://localhost:8000`

To change, edit in `dashboard/app.py`:
```python
API_URL = "http://your-api-url:port"
```

### Port
Default: `8501`

To change:
```bash
streamlit run dashboard/app.py --server.port 8502
```

## 📁 Files

- `app.py` - Main Streamlit application (800+ lines)
- `README.md` - This file

## 🔧 Requirements

See `requirements-dashboard.txt`:
- streamlit >= 1.28.0
- plotly >= 5.17.0
- folium >= 0.14.0
- streamlit-folium >= 0.15.0
- requests >= 2.31.0

## 🐛 Troubleshooting

### API Connection Failed
Make sure the API is running:
```bash
python start_api.py
```

### Data Files Not Found
Ensure `passengers.csv` and `bus.csv` are in the project root.

### Charts Not Rendering
Update Plotly:
```bash
pip install --upgrade plotly
```

## 📚 Documentation

Full documentation: See `PHASE6.5_DASHBOARD_SUMMARY.md` in project root

## 🎯 Usage Tips

1. **Start with Home page** to see overview
2. **Explore data** in Data Explorer before making predictions
3. **Check API status** in sidebar before using Prediction Tool
4. **Use presets** in Prediction Tool for quick testing
5. **Monitor metrics** in API Monitor to track usage

## 🎨 Customization

### Change Colors
Edit CSS in `app.py`:
```python
st.markdown("""
<style>
    .main-header {
        color: #your-color;
    }
</style>
""", unsafe_allow_html=True)
```

### Add New Page
1. Add option in sidebar radio button
2. Create page content function
3. Add elif block in main content area

## ✨ Example Workflow

```python
# 1. Start API (in terminal 1)
python start_api.py

# 2. Start dashboard (in terminal 2)
python start_dashboard.py

# 3. Use dashboard:
#    - View data in Data Explorer
#    - Test predictions in Prediction Tool
#    - Monitor API in API Monitor
```

## 📊 Data Sources

### Historical Data (50K+ records)
- `passengers.csv` - Passenger GPS data
- `bus.csv` - Bus GPS data
- `models/metrics.json` - Model performance

### Real-time Data
- API predictions via `/predict/single`
- API metrics via `/metrics`

## 🔐 Security Note

**Current setup is for local development only!**

For production:
- Add authentication
- Use HTTPS
- Secure API endpoints
- Implement rate limiting

## 🎉 Success Checklist

- [ ] All 6 pages load without errors
- [ ] API status shows ✅ green
- [ ] Charts render correctly
- [ ] Predictions work in Prediction Tool
- [ ] Metrics display in API Monitor

## 📈 Performance

- **Load Time**: < 2 seconds (with caching)
- **Page Switch**: Instant
- **API Call**: < 1 second
- **Map Render**: 1-3 seconds (depends on sample size)

## 🤝 Support

Issues? Check:
1. API is running (`http://localhost:8000/health`)
2. Data files exist (`passengers.csv`, `bus.csv`)
3. Dependencies installed (`pip list | findstr streamlit`)
4. Browser console for errors (F12)

---

Built with ❤️ using Streamlit | Part of MLOps Pipeline Phase 6.5
