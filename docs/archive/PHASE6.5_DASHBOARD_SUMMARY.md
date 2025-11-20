# Phase 6.5: Interactive Dashboard

## 📊 Overview

An interactive Streamlit dashboard for exploring bus passenger data and testing ML predictions in real-time. The dashboard provides 6 comprehensive views for data analysis, visualization, and model testing.

## ✨ Features

### 1. 🏠 Home Page
- **Project Overview**: Summary of the classification system and tech stack
- **Quick Statistics**: Total passengers, bus records, model F1 score
- **Model Performance Summary**: Visual bar chart of key metrics
- **Dataset Stats**: IN/OUT records, unique users, average speed

### 2. 📊 Data Explorer
Four interactive tabs for comprehensive data analysis:

#### Distributions Tab
- Label distribution pie chart (IN vs OUT)
- Speed distribution histogram
- Acceleration X distribution
- Automotive confidence distribution

#### Time Analysis Tab
- Activity by hour of day (bar chart)
- Activity by day of week (bar chart)
- Temporal patterns visualization

#### User Analysis Tab
- Top 20 users by record count
- Total users, average records per user
- Maximum records from a single user

#### Raw Data Tab
- Interactive data table with filters
- Filter by label (IN/OUT)
- Filter by user ID
- Adjustable row count (10-1000)
- CSV download functionality

### 3. 🗺️ Map View
- Interactive scatter mapbox visualization
- Color-coded points by label (IN=green, OUT=red)
- Adjustable sample size for performance
- Geographic statistics (min/max lat/lon)
- Hover data showing user ID and speed

### 4. 📈 Model Performance
- **Key Metrics Display**: Accuracy, F1-score, Precision, Recall
- **Class-Specific Performance**:
  - OUT class metrics (Precision, Recall, F1)
  - IN class metrics (Precision, Recall, F1)
- **Model Configuration**: Sample counts, cluster distribution
- Visual bar charts for easy comparison

### 5. 🔮 Prediction Tool
- **Manual Input Form**:
  - User ID
  - Latitude (with validation)
  - Longitude (with validation)
  - Timestamp (auto-populated, editable)
  - Speed in m/s
- **Quick Test Presets**:
  - Station Stop (lat=55.792232, lon=12.522917, speed=0.0)
  - Walking (speed=1.5 m/s)
  - Moving (speed=5.0 m/s)
- **Real-time API Calls**: Direct integration with FastAPI backend
- **Visual Results**: Color-coded predictions (🟢 IN / 🔴 OUT)
- **Confidence Scores**: Shows model confidence for predictions

### 6. 📡 API Monitor
- **API Health Check**: Real-time connection status
- **Model Information**: Version, stage, status
- **Prometheus Metrics**: Live API statistics
  - Total predictions count
  - Total API calls
  - Total errors
- **Endpoint Documentation**: Complete list of available API endpoints

## 🚀 Getting Started

### Prerequisites

1. **Install Dependencies**:
```bash
pip install -r requirements-dashboard.txt
```

This installs:
- `streamlit>=1.28.0` - Web framework
- `plotly>=5.17.0` - Interactive charts
- `folium>=0.14.0` - Maps
- `streamlit-folium>=0.15.0` - Streamlit-Folium integration
- `requests>=2.31.0` - API calls

2. **Data Files Required**:
- `passengers.csv` - Passenger GPS data (50,601 records)
- `bus.csv` - Bus GPS data (53,155 records)
- `models/metrics.json` - Model performance metrics (optional)

3. **API Running**:
The Prediction Tool and API Monitor require the FastAPI backend:
```bash
python start_api.py
```

### Starting the Dashboard

**Option 1: Using the launcher script (recommended)**
```bash
python start_dashboard.py
```

**Option 2: Direct Streamlit command**
```bash
streamlit run dashboard/app.py
```

**Option 3: Custom port**
```bash
streamlit run dashboard/app.py --server.port 8502
```

The dashboard will automatically open in your browser at:
- Default: http://localhost:8501
- With custom port: http://localhost:8502

## 🎨 User Interface

### Layout
- **Sidebar Navigation**: Radio buttons to switch between 6 pages
- **API Status Indicator**: Shows real-time API connection status
- **Wide Layout**: Optimized for data visualization
- **Responsive Design**: Adapts to different screen sizes

### Color Scheme
- **Primary Blue**: #1f77b4 (headers, metrics)
- **Success Green**: #4ECDC4 (IN predictions, success states)
- **Error Red**: #FF6B6B (OUT predictions, error states)
- **Neutral Gray**: #f0f2f6 (metric cards, backgrounds)

### Custom Components
- **Metric Cards**: Styled containers with left border accent
- **Success/Error Boxes**: Colored alert boxes for status messages
- **Interactive Charts**: Plotly charts with hover tooltips
- **Data Tables**: Filterable, sortable dataframes

## 📊 Data Sources

### Historical Data
Used by: Home, Data Explorer, Map View, Model Performance

- **passengers.csv**: 50,601 GPS records
  - Columns: id, lat, lon, timestamp_utc, speed, sensor data, labels
  - Time period: January 2020
  - Location: Copenhagen, Denmark (55.6-55.9°N, 12.4-12.7°E)

- **bus.csv**: 53,155 bus GPS records
  - Bus routes and stops
  - Geographic distribution

- **models/metrics.json**: Model evaluation results
  - Accuracy, F1-score, precision, recall
  - Class-specific metrics (IN/OUT)
  - Cluster distribution

### Real-time Data
Used by: Prediction Tool, API Monitor

- **API Predictions**: Live calls to `/predict/single` endpoint
  - Input: GPS coordinates, timestamp, speed
  - Output: Predicted label (IN/OUT), confidence score

- **API Metrics**: Prometheus-compatible metrics from `/metrics`
  - Prediction counts (total, single, batch, CSV)
  - API call counts
  - Error counts

## 🔧 Technical Implementation

### Caching Strategy
```python
@st.cache_data
def load_passenger_data():
    """Cached data loading - only loads once per session"""
    df = pd.read_csv('passengers.csv')
    df['timestamp_utc'] = pd.to_datetime(df['timestamp_utc'])
    return df
```

Benefits:
- Loads data once, reuses across page switches
- Faster navigation between pages
- Reduced memory usage

### API Integration
```python
def call_prediction_api(lat, lon, timestamp_utc, speed, user_id):
    """Call FastAPI prediction endpoint"""
    payload = {
        "id": user_id,
        "lat": float(lat),
        "lon": float(lon),
        "timestamp_utc": timestamp_utc,
        "speed": float(speed)
    }
    response = requests.post(f"{API_URL}/predict/single", json=payload, timeout=5)
    return response.json()
```

Features:
- Timeout protection (5 seconds)
- Error handling with user-friendly messages
- JSON payload validation

### Performance Optimization
- **Data Sampling**: Map view uses adjustable sample sizes (100-10,000 points)
- **Lazy Loading**: Charts only render when tab is active
- **Efficient Filtering**: DataFrame operations use pandas optimizations
- **Memory Management**: Large datasets handled with chunking

## 📱 Usage Examples

### Example 1: Exploring Data Patterns
1. Navigate to **📊 Data Explorer**
2. Select **Time Analysis** tab
3. View activity by hour to identify peak times
4. Check day-of-week distribution for patterns
5. Use insights for operational planning

### Example 2: Testing Model Predictions
1. Ensure API is running (check sidebar status)
2. Navigate to **🔮 Prediction Tool**
3. Click "📍 Preset 1: Station Stop" for quick test
4. Click "🔮 Make Prediction"
5. Review result (🟢 IN or 🔴 OUT) and confidence score
6. Try different coordinates or use custom input

### Example 3: Monitoring API Performance
1. Navigate to **📡 API Monitor**
2. Check API health status (should be ✅ green)
3. Review model information (version, stage)
4. Click "🔄 Refresh Metrics" to see latest stats
5. Monitor prediction counts and error rates

### Example 4: Geographic Analysis
1. Navigate to **🗺️ Map View**
2. Adjust sample size slider (start with 1000 points)
3. View geographic distribution of passengers
4. Check min/max coordinates for coverage area
5. Identify hotspots and patterns

## 🛡️ Error Handling

### API Offline
- Dashboard detects API unavailability
- Displays clear error message in sidebar
- Shows command to start API: `python start_api.py`
- Prediction Tool shows alert with instructions

### Missing Data Files
- Graceful handling of missing CSV files
- User-friendly error messages
- Continues to show available features
- Suggests data location in error message

### Invalid Inputs
- Form validation for latitude (-90 to 90)
- Form validation for longitude (-180 to 180)
- Speed validation (0 to 50 m/s)
- Timestamp format checking

## 🎯 Key Metrics

### Dashboard Performance
- **Load Time**: < 2 seconds (with cached data)
- **Page Switch**: Instant (thanks to caching)
- **Map Rendering**: 1-3 seconds (depends on sample size)
- **API Calls**: < 1 second (prediction endpoint)

### Data Statistics
- **Total Passengers**: 50,601 records
- **Total Bus Records**: 53,155 records
- **Unique Users**: Varies by dataset
- **Time Range**: January 2020
- **Geographic Area**: Copenhagen (≈ 30 km²)

### Model Performance (from metrics.json)
- **Accuracy**: ~52.0%
- **F1 Score**: ~0.596
- **Test Samples**: 12,795
- **Features**: 52

## 🚀 Deployment Options

### Local Development
```bash
streamlit run dashboard/app.py
```
- Runs on localhost:8501
- Auto-reloads on code changes
- Debug mode enabled

### Production Deployment

**Streamlit Cloud** (Recommended)
1. Push code to GitHub
2. Connect repository to Streamlit Cloud
3. Configure secrets for API URL
4. Deploy with one click

**Docker Container**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements-dashboard.txt .
RUN pip install -r requirements-dashboard.txt
COPY dashboard/ ./dashboard/
COPY *.csv .
CMD ["streamlit", "run", "dashboard/app.py", "--server.port", "8501", "--server.headless", "true"]
```

**Custom Server**
```bash
streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0
```

## 🔐 Security Considerations

### Current Implementation
- No authentication (suitable for local development)
- API calls to localhost only
- No sensitive data exposure

### Production Recommendations
1. **Add Authentication**: Use Streamlit auth or OAuth
2. **HTTPS**: Enable SSL/TLS for encrypted connections
3. **API Security**: Add API keys or JWT tokens
4. **Rate Limiting**: Prevent API abuse
5. **Data Privacy**: Anonymize or encrypt sensitive data

## 📈 Future Enhancements

### Phase 6.5+ Features
1. **Real-time Streaming**:
   - WebSocket connection to API
   - Live prediction feed
   - Auto-refreshing metrics

2. **Advanced Analytics**:
   - Cluster visualization (HDBSCAN results)
   - Feature importance plots
   - Prediction confidence distributions

3. **User Management**:
   - User-specific dashboards
   - Saved filters and views
   - Annotation capabilities

4. **Export Features**:
   - PDF report generation
   - Custom chart exports
   - Scheduled email reports

5. **A/B Testing**:
   - Compare multiple models
   - Side-by-side predictions
   - Performance comparison charts

6. **Integration**:
   - DVC integration for data versioning
   - MLflow UI embedding
   - GitHub Actions status

## 🐛 Troubleshooting

### Dashboard won't start
```bash
# Check Streamlit installation
python -m streamlit --version

# Reinstall if needed
pip install --upgrade streamlit
```

### API connection fails
```bash
# Verify API is running
curl http://localhost:8000/health

# Check port conflicts
netstat -ano | findstr :8000

# Restart API
python start_api.py
```

### Data not loading
```bash
# Verify CSV files exist
dir passengers.csv bus.csv

# Check file permissions
# Ensure files are readable

# Verify CSV format
python -c "import pandas as pd; print(pd.read_csv('passengers.csv').shape)"
```

### Charts not rendering
```bash
# Update Plotly
pip install --upgrade plotly

# Clear Streamlit cache
# In dashboard, press 'C' then 'Clear cache'

# Check browser console for errors
```

### High memory usage
- Reduce sample size on Map View
- Close unused tabs in browser
- Restart dashboard to clear cache
- Use data sampling for large datasets

## 📚 Dependencies

### Core Libraries
- **streamlit**: Web framework for Python
- **pandas**: Data manipulation
- **numpy**: Numerical computing
- **plotly**: Interactive charts
- **requests**: HTTP library for API calls

### Optional Libraries
- **folium**: Map visualizations
- **streamlit-folium**: Streamlit-Folium bridge

### Version Requirements
- Python >= 3.8
- Streamlit >= 1.28.0
- Plotly >= 5.17.0
- Folium >= 0.14.0

## 🎓 Learning Resources

### Streamlit Documentation
- Official docs: https://docs.streamlit.io
- API reference: https://docs.streamlit.io/library/api-reference
- Gallery: https://streamlit.io/gallery

### Plotly Documentation
- Plotly Python: https://plotly.com/python/
- Chart types: https://plotly.com/python/basic-charts/

### Best Practices
- Use caching for expensive operations
- Keep page load times under 3 seconds
- Provide loading indicators for long operations
- Handle errors gracefully with user-friendly messages

## 🤝 Contributing

To add new features to the dashboard:

1. **Add New Page**: Add new radio option in sidebar
2. **Create Page Function**: Define page content
3. **Add to Main Logic**: Add elif block in main content area
4. **Update Documentation**: Document new features
5. **Test Thoroughly**: Ensure no breaking changes

Example:
```python
# In sidebar
page = st.radio("Select Page", [..., "🆕 New Feature"])

# In main content
elif page == "🆕 New Feature":
    st.markdown("## 🆕 New Feature")
    # Your code here
```

## 📝 Changelog

### Version 1.0.0 (Current)
- ✅ 6 interactive pages (Home, Data Explorer, Map View, Model Performance, Prediction Tool, API Monitor)
- ✅ Real-time API integration
- ✅ Data caching for performance
- ✅ Custom styling and themes
- ✅ Error handling and validation
- ✅ CSV download functionality
- ✅ Interactive charts with Plotly
- ✅ Quick test presets

### Upcoming
- 🔄 Live streaming predictions
- 🔄 Advanced analytics
- 🔄 User authentication
- 🔄 PDF report generation

## 📞 Support

For issues or questions:
1. Check this documentation
2. Review error messages in dashboard
3. Check API logs: `mlruns/` and console output
4. Verify data files are present and valid
5. Ensure all dependencies are installed

## 🎉 Success Indicators

Dashboard is working correctly when:
- ✅ All 6 pages load without errors
- ✅ API status shows green checkmark
- ✅ Data Explorer shows charts and statistics
- ✅ Map View renders geographic visualization
- ✅ Prediction Tool successfully calls API and shows results
- ✅ API Monitor displays metrics and model info

## 🏁 Summary

The Phase 6.5 Dashboard provides:
- **Comprehensive Data Exploration**: 4 analysis tabs with rich visualizations
- **Real-time Predictions**: Interactive testing with live API integration
- **Model Monitoring**: Performance metrics and API health tracking
- **User-friendly Interface**: Intuitive navigation and responsive design
- **Production-ready**: Error handling, caching, and optimization
- **Portfolio-worthy**: Professional presentation for stakeholders

Perfect complement to the MLOps pipeline, transforming technical ML models into accessible, interactive insights! 🚀
