"""
Bus Passenger Classifier Dashboard
Interactive dashboard for data exploration and real-time predictions
"""

import warnings

warnings.filterwarnings("ignore")

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import requests
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Page configuration
st.set_page_config(
    page_title="Bus Passenger Classifier",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# API Configuration
API_URL = "http://localhost:8000"

# Custom CSS
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        color: #155724;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        color: #721c24;
    }
</style>
""",
    unsafe_allow_html=True,
)


# Cache data loading
@st.cache_data
def load_passenger_data():
    """Load passenger data from CSV file"""
    try:
        df = pd.read_csv("passengers.csv")
        # Use format='ISO8601' to handle mixed timestamp formats
        if "timestamp_utc" in df.columns:
            df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], format="ISO8601")
        return df
    except Exception as e:
        st.error(f"Error loading passenger data: {e}")
        return None


@st.cache_data
def load_bus_data():
    """Load bus data from CSV file"""
    try:
        df = pd.read_csv("bus.csv")
        if "timestamp_utc" in df.columns:
            # Use format='ISO8601' to handle mixed timestamp formats
            df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], format="ISO8601")
        return df
    except Exception as e:
        st.error(f"Error loading bus data: {e}")
        return None


@st.cache_data
def load_model_metrics():
    """Load model metrics if available"""
    try:
        with open("models/metrics.json", "r") as f:
            return json.load(f)
    except:
        return None


def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200, (
            response.json() if response.status_code == 200 else None
        )
    except:
        return False, None


def call_prediction_api(lat, lon, timestamp_utc, speed=0.0, user_id="dashboard_user"):
    """Call prediction API"""
    try:
        payload = {
            "id": user_id,  # Only send id, API will create user_id
            "lat": float(lat),
            "lon": float(lon),
            "timestamp_utc": timestamp_utc,
            "speed": float(speed),
        }
        response = requests.post(f"{API_URL}/predict/single", json=payload, timeout=5)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()
    except Exception as e:
        return False, str(e)


# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/bus.png", width=80)
    st.markdown("## 🚌 Navigation")

    page = st.radio(
        "Select Page",
        [
            "🏠 Home",
            "📊 Data Explorer",
            "🗺️ Map View",
            "📈 Model Performance",
            "🔮 Prediction Tool",
            "📡 API Monitor",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")

    # API Status
    st.markdown("### 📡 API Status")
    api_healthy, api_info = check_api_health()
    if api_healthy:
        st.markdown(
            '<div class="success-box">✅ API Online</div>', unsafe_allow_html=True
        )
        if api_info and "model_info" in api_info:
            model_info = api_info["model_info"]
            st.caption(f"Model: {model_info.get('model_name', 'N/A')}")
            st.caption(f"Version: {model_info.get('version', 'N/A')}")
            st.caption(f"Stage: {model_info.get('stage', 'N/A')}")
    else:
        st.markdown(
            '<div class="error-box">❌ API Offline</div>', unsafe_allow_html=True
        )
        st.caption("Start API: `python start_api.py`")

    st.markdown("---")

    # Quick Links
    st.markdown("### 🔗 Quick Links")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📈 MLflow UI", width="stretch"):
            st.markdown("[Open MLflow](http://localhost:5000)", unsafe_allow_html=True)
    with col2:
        if st.button("🚀 FastAPI", width="stretch"):
            st.markdown(
                "[Open API Docs](http://localhost:8000/docs)", unsafe_allow_html=True
            )

    # Direct links (always visible)
    st.markdown("- [MLflow UI](http://localhost:5000) - Experiment tracking")
    st.markdown("- [FastAPI Docs](http://localhost:8000/docs) - API documentation")
    st.markdown("- [API Health](http://localhost:8000/health) - API status")

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.caption(
        "Real-time bus passenger classification using GPS data and machine learning."
    )
    st.caption("Built with MLflow, DVC, FastAPI & Streamlit")

# Main content
st.markdown(
    '<h1 class="main-header">🚌 Bus Passenger Classifier Dashboard</h1>',
    unsafe_allow_html=True,
)

# ========================
# HOME PAGE
# ========================
if page == "🏠 Home":
    st.markdown("## Welcome to the Bus Passenger Classification System")

    col1, col2, col3 = st.columns(3)

    # Load data for stats
    passengers_df = load_passenger_data()
    bus_df = load_bus_data()
    metrics = load_model_metrics()

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            "Total Passengers",
            f"{len(passengers_df):,}" if passengers_df is not None else "N/A",
            help="Total passenger GPS records",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            "Bus Records",
            f"{len(bus_df):,}" if bus_df is not None else "N/A",
            help="Total bus GPS records",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            "Model F1 Score",
            f"{metrics.get('f1_score', 0):.3f}" if metrics else "N/A",
            help="Model performance metric",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Project Overview
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📋 Project Overview")
        st.markdown(
            """
        This system classifies bus passengers as **IN** or **OUT** based on GPS data using:
        
        - 🎯 **HDBSCAN Clustering** for pattern detection
        - 📊 **Feature Engineering** (speed, acceleration, bearing, distance)
        - 🔬 **PCA** for dimensionality reduction
        - 📈 **MLflow** for experiment tracking
        - 🗄️ **DVC** for data versioning
        - 🚀 **FastAPI** for real-time predictions
        
        **Use the sidebar to navigate through different sections!**
        """
        )

    with col2:
        st.markdown("### 🎯 Model Performance")
        if metrics:
            perf_data = {
                "Metric": [
                    "Accuracy",
                    "F1 Score",
                    "Precision (OUT)",
                    "Recall (OUT)",
                    "Precision (IN)",
                    "Recall (IN)",
                ],
                "Value": [
                    metrics.get("accuracy", 0),
                    metrics.get("f1_score", 0),
                    metrics.get("precision_out", 0),
                    metrics.get("recall_out", 0),
                    metrics.get("precision_in", 0),
                    metrics.get("recall_in", 0),
                ],
            }
            perf_df = pd.DataFrame(perf_data)

            fig = px.bar(
                perf_df,
                x="Metric",
                y="Value",
                color="Value",
                color_continuous_scale="Blues",
                range_y=[0, 1],
            )
            fig.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("Model metrics not available. Train a model first.")

    st.markdown("---")

    # Quick Stats
    if passengers_df is not None:
        st.markdown("### 📊 Quick Statistics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if "label" in passengers_df.columns:
                label_counts = passengers_df["label"].value_counts()
                st.metric("IN Records", f"{label_counts.get('IN', 0):,}")

        with col2:
            if "label" in passengers_df.columns:
                label_counts = passengers_df["label"].value_counts()
                st.metric("OUT Records", f"{label_counts.get('OUT', 0):,}")

        with col3:
            unique_users = passengers_df["id"].nunique()
            st.metric("Unique Users", f"{unique_users:,}")

        with col4:
            if "speed" in passengers_df.columns:
                avg_speed = passengers_df["speed"].mean()
                st.metric("Avg Speed", f"{avg_speed:.2f} m/s")

# ========================
# DATA EXPLORER PAGE
# ========================
elif page == "📊 Data Explorer":
    st.markdown("## 📊 Data Exploration")

    passengers_df = load_passenger_data()

    if passengers_df is None:
        st.error(
            "Unable to load passenger data. Please check if passengers.csv exists."
        )
    else:
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(
            ["📈 Distributions", "🕐 Time Analysis", "👥 User Analysis", "📋 Raw Data"]
        )

        with tab1:
            st.markdown("### Distribution Analysis")

            col1, col2 = st.columns(2)

            with col1:
                # Label distribution
                if "label" in passengers_df.columns:
                    st.markdown("#### Label Distribution")
                    label_counts = passengers_df["label"].value_counts()
                    fig = px.pie(
                        values=label_counts.values,
                        names=label_counts.index,
                        title="IN vs OUT Distribution",
                        color_discrete_sequence=["#FF6B6B", "#4ECDC4"],
                    )
                    st.plotly_chart(fig, width="stretch")
                else:
                    st.info("No label column found in data")

            with col2:
                # Speed distribution
                if "speed" in passengers_df.columns:
                    st.markdown("#### Speed Distribution")
                    fig = px.histogram(
                        passengers_df,
                        x="speed",
                        nbins=50,
                        title="Speed Distribution (m/s)",
                        color_discrete_sequence=["#1f77b4"],
                    )
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, width="stretch")

            # Additional distributions
            col3, col4 = st.columns(2)

            with col3:
                if "accx" in passengers_df.columns:
                    st.markdown("#### Acceleration X Distribution")
                    fig = px.histogram(
                        passengers_df.sample(min(5000, len(passengers_df))),
                        x="accx",
                        nbins=50,
                        color_discrete_sequence=["#2ecc71"],
                    )
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, width="stretch")

            with col4:
                if "automotive" in passengers_df.columns:
                    st.markdown("#### Automotive Confidence")
                    fig = px.histogram(
                        passengers_df.sample(min(5000, len(passengers_df))),
                        x="automotive",
                        nbins=50,
                        color_discrete_sequence=["#e74c3c"],
                    )
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, width="stretch")

        with tab2:
            st.markdown("### Time-based Analysis")

            if "timestamp_utc" in passengers_df.columns:
                # Extract hour
                passengers_df["hour"] = passengers_df["timestamp_utc"].dt.hour
                passengers_df["day"] = passengers_df["timestamp_utc"].dt.day_name()

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### Activity by Hour")
                    hourly_counts = passengers_df["hour"].value_counts().sort_index()
                    fig = px.bar(
                        x=hourly_counts.index,
                        y=hourly_counts.values,
                        labels={"x": "Hour of Day", "y": "Number of Records"},
                        color=hourly_counts.values,
                        color_continuous_scale="Blues",
                    )
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, width="stretch")

                with col2:
                    st.markdown("#### Activity by Day of Week")
                    day_order = [
                        "Monday",
                        "Tuesday",
                        "Wednesday",
                        "Thursday",
                        "Friday",
                        "Saturday",
                        "Sunday",
                    ]
                    day_counts = passengers_df["day"].value_counts()
                    day_counts = day_counts.reindex(
                        [d for d in day_order if d in day_counts.index]
                    )

                    fig = px.bar(
                        x=day_counts.index,
                        y=day_counts.values,
                        labels={"x": "Day of Week", "y": "Number of Records"},
                        color=day_counts.values,
                        color_continuous_scale="Greens",
                    )
                    fig.update_layout(showlegend=False, xaxis_tickangle=-45)
                    st.plotly_chart(fig, width="stretch")

        with tab3:
            st.markdown("### User Analysis")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Records per User")
                user_counts = passengers_df["id"].value_counts().head(20)
                fig = px.bar(
                    x=user_counts.index.astype(str),
                    y=user_counts.values,
                    labels={"x": "User ID", "y": "Number of Records"},
                    color=user_counts.values,
                    color_continuous_scale="Reds",
                )
                fig.update_layout(showlegend=False, xaxis_tickangle=-45)
                st.plotly_chart(fig, width="stretch")

            with col2:
                st.markdown("#### Statistics")
                st.metric("Total Users", passengers_df["id"].nunique())
                st.metric(
                    "Avg Records/User",
                    f"{len(passengers_df) / passengers_df['id'].nunique():.1f}",
                )
                st.metric(
                    "Max Records (Single User)",
                    passengers_df["id"].value_counts().max(),
                )

        with tab4:
            st.markdown("### Raw Data Sample")

            # Add filters
            col1, col2, col3 = st.columns(3)

            with col1:
                if "label" in passengers_df.columns:
                    label_filter = st.multiselect(
                        "Filter by Label",
                        options=passengers_df["label"].unique(),
                        default=list(passengers_df["label"].unique()),
                    )
                else:
                    label_filter = None

            with col2:
                user_ids = passengers_df["id"].unique()[:100]  # Limit for performance
                user_filter = st.multiselect(
                    "Filter by User ID", options=user_ids, default=[]
                )

            with col3:
                n_rows = st.slider("Number of rows", 10, 1000, 100)

            # Apply filters
            filtered_df = passengers_df.copy()
            if label_filter and "label" in passengers_df.columns:
                filtered_df = filtered_df[filtered_df["label"].isin(label_filter)]
            if user_filter:
                filtered_df = filtered_df[filtered_df["id"].isin(user_filter)]

            st.dataframe(filtered_df.head(n_rows), width="stretch")

            # Download button
            csv = filtered_df.head(n_rows).to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"passenger_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )

# ========================
# MAP VIEW PAGE
# ========================
elif page == "🗺️ Map View":
    st.markdown("## 🗺️ Geographic Visualization")

    passengers_df = load_passenger_data()

    if passengers_df is None:
        st.error("Unable to load passenger data.")
    else:
        st.info("🗺️ Map visualization requires folium. Showing scatter plot instead.")

        # Sample data for performance
        sample_size = st.slider(
            "Sample Size", 100, 10000, 1000, help="Number of points to display"
        )
        sample_df = passengers_df.sample(min(sample_size, len(passengers_df)))

        # Color by label if available
        if "label" in sample_df.columns:
            color_col = "label"
            color_map = {"IN": "#4ECDC4", "OUT": "#FF6B6B"}
        else:
            color_col = None
            color_map = None

        fig = px.scatter_mapbox(
            sample_df,
            lat="lat",
            lon="lon",
            color=color_col if color_col else None,
            color_discrete_map=color_map,
            hover_data=["id", "speed"] if "speed" in sample_df.columns else ["id"],
            zoom=11,
            height=600,
            title=f"GPS Points (Sample of {len(sample_df)} points)",
        )

        fig.update_layout(
            mapbox_style="open-street-map", margin={"r": 0, "t": 40, "l": 0, "b": 0}
        )

        st.plotly_chart(fig, width="stretch")

        # Geographic statistics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Min Latitude", f"{passengers_df['lat'].min():.6f}")
        with col2:
            st.metric("Max Latitude", f"{passengers_df['lat'].max():.6f}")
        with col3:
            st.metric("Min Longitude", f"{passengers_df['lon'].min():.6f}")
        with col4:
            st.metric("Max Longitude", f"{passengers_df['lon'].max():.6f}")

# ========================
# MODEL PERFORMANCE PAGE
# ========================
elif page == "📈 Model Performance":
    st.markdown("## 📈 Model Performance Analysis")

    metrics = load_model_metrics()

    if metrics is None:
        st.warning(
            "Model metrics not found. Train a model first using `python src/train_mlflow.py`"
        )
    else:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Accuracy", f"{metrics.get('accuracy', 0):.4f}")
        with col2:
            st.metric("F1 Score", f"{metrics.get('f1_score', 0):.4f}")
        with col3:
            st.metric("Precision (Macro)", f"{metrics.get('precision', 0):.4f}")
        with col4:
            st.metric("Recall (Macro)", f"{metrics.get('recall', 0):.4f}")

        st.markdown("---")

        # Class-specific metrics
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### OUT Class Performance")
            out_metrics = {
                "Metric": ["Precision", "Recall", "F1-Score"],
                "Value": [
                    metrics.get("precision_out", 0),
                    metrics.get("recall_out", 0),
                    metrics.get("f1_out", 0),
                ],
            }
            fig = px.bar(
                out_metrics,
                x="Metric",
                y="Value",
                color="Value",
                color_continuous_scale="Reds",
                range_y=[0, 1],
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, width="stretch")

        with col2:
            st.markdown("### IN Class Performance")
            in_metrics = {
                "Metric": ["Precision", "Recall", "F1-Score"],
                "Value": [
                    metrics.get("precision_in", 0),
                    metrics.get("recall_in", 0),
                    metrics.get("f1_in", 0),
                ],
            }
            fig = px.bar(
                in_metrics,
                x="Metric",
                y="Value",
                color="Value",
                color_continuous_scale="Greens",
                range_y=[0, 1],
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, width="stretch")

        st.markdown("---")

        # Additional metrics
        st.markdown("### Model Configuration")

        col1, col2 = st.columns(2)

        with col1:
            st.json(
                {
                    "Total Samples": metrics.get("total_samples", "N/A"),
                    "Training Samples": metrics.get("train_samples", "N/A"),
                    "Test Samples": metrics.get("test_samples", "N/A"),
                }
            )

        with col2:
            if "cluster_counts" in metrics:
                st.markdown("#### Cluster Distribution")
                cluster_data = metrics["cluster_counts"]
                fig = px.pie(
                    values=list(cluster_data.values()),
                    names=list(cluster_data.keys()),
                    title="Predicted Clusters",
                )
                st.plotly_chart(fig, width="stretch")

# ========================
# PREDICTION TOOL PAGE
# ========================
elif page == "🔮 Prediction Tool":
    st.markdown("## 🔮 Real-Time Prediction Tool")

    api_healthy, api_info = check_api_health()

    if not api_healthy:
        st.error("⚠️ API is not running. Please start the API first:")
        st.code("python start_api.py", language="bash")
    else:
        st.success("✅ API is online and ready!")

        st.markdown("### Enter GPS Data for Prediction")

        col1, col2 = st.columns(2)

        with col1:
            user_id = st.text_input(
                "User ID", value="dashboard_test", help="Unique identifier for the user"
            )
            lat = st.number_input(
                "Latitude",
                min_value=-90.0,
                max_value=90.0,
                value=55.792232,
                format="%.6f",
                help="Latitude in degrees (Copenhagen area: 55.6-55.9)",
            )
            lon = st.number_input(
                "Longitude",
                min_value=-180.0,
                max_value=180.0,
                value=12.522917,
                format="%.6f",
                help="Longitude in degrees (Copenhagen area: 12.4-12.7)",
            )

        with col2:
            timestamp = st.text_input(
                "Timestamp (UTC)",
                value=datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f+00:00"),
                help="ISO format timestamp with timezone",
            )
            speed = st.number_input(
                "Speed (m/s)",
                min_value=0.0,
                max_value=50.0,
                value=0.0,
                format="%.2f",
                help="Speed in meters per second",
            )

        st.markdown("---")

        # Quick presets
        st.markdown("### 🎯 Quick Test Presets")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📍 Preset 1: Station Stop"):
                lat = 55.792232
                lon = 12.522917
                speed = 0.0
                st.rerun()

        with col2:
            if st.button("🚶 Preset 2: Walking"):
                lat = 55.792244
                lon = 12.522932
                speed = 1.5
                st.rerun()

        with col3:
            if st.button("🚗 Preset 3: Moving"):
                lat = 55.792243
                lon = 12.522934
                speed = 5.0
                st.rerun()

        st.markdown("---")

        # Prediction button
        if st.button("🔮 Make Prediction", type="primary", width="stretch"):
            with st.spinner("Calling API..."):
                success, result = call_prediction_api(
                    lat, lon, timestamp, speed, user_id
                )

            if success:
                st.markdown("### 🎉 Prediction Result")

                predicted_label = result.get("predicted_label", -1)
                confidence = result.get("confidence")

                # Display result with color
                if predicted_label == 0:
                    st.markdown(
                        '<div class="error-box"><h2>🔴 OUT - Passenger Getting Off</h2></div>',
                        unsafe_allow_html=True,
                    )
                elif predicted_label == 1:
                    st.markdown(
                        '<div class="success-box"><h2>🟢 IN - Passenger Getting On</h2></div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.warning(f"Unknown prediction: {predicted_label}")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Predicted Label", predicted_label)
                    if confidence is not None:
                        st.metric("Confidence Score", f"{confidence:.4f}")

                with col2:
                    st.json(
                        {
                            "user_id": result.get("user_id"),
                            "model_info": result.get("model_info", {}),
                        }
                    )
            else:
                st.error(f"❌ Prediction failed: {result}")

# ========================
# API MONITOR PAGE
# ========================
elif page == "📡 API Monitor":
    st.markdown("## 📡 API Monitoring")

    api_healthy, api_info = check_api_health()

    if not api_healthy:
        st.error("⚠️ API is offline")
    else:
        st.success("✅ API is online")

        # Display API info
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### API Health")
            st.json(api_info)

        with col2:
            st.markdown("### Model Information")
            try:
                response = requests.get(f"{API_URL}/model/info", timeout=2)
                if response.status_code == 200:
                    st.json(response.json())
                else:
                    st.error("Unable to fetch model info")
            except:
                st.error("API request failed")

        st.markdown("---")

        # Metrics endpoint
        st.markdown("### 📊 Prometheus Metrics")

        if st.button("🔄 Refresh Metrics"):
            try:
                response = requests.get(f"{API_URL}/metrics", timeout=2)
                if response.status_code == 200:
                    metrics_text = response.text
                    st.code(metrics_text, language="text")

                    # Parse and visualize
                    lines = metrics_text.strip().split("\n")
                    metric_values = {}
                    for line in lines:
                        if not line.startswith("#") and line.strip():
                            parts = line.split()
                            if len(parts) == 2:
                                metric_values[parts[0]] = float(parts[1])

                    if metric_values:
                        st.markdown("### 📈 Metrics Visualization")

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric(
                                "Total Predictions",
                                int(metric_values.get("predictions_total", 0)),
                            )
                        with col2:
                            st.metric(
                                "Total API Calls",
                                int(metric_values.get("api_calls_total", 0)),
                            )
                        with col3:
                            st.metric(
                                "Total Errors",
                                int(metric_values.get("errors_total", 0)),
                            )
                else:
                    st.error("Unable to fetch metrics")
            except Exception as e:
                st.error(f"Error: {e}")

        st.markdown("---")

        # API endpoints documentation
        st.markdown("### 📚 Available Endpoints")

        endpoints = [
            {"Method": "GET", "Endpoint": "/", "Description": "Root endpoint"},
            {"Method": "GET", "Endpoint": "/health", "Description": "Health check"},
            {
                "Method": "GET",
                "Endpoint": "/model/info",
                "Description": "Model information",
            },
            {
                "Method": "POST",
                "Endpoint": "/predict/single",
                "Description": "Single prediction",
            },
            {
                "Method": "POST",
                "Endpoint": "/predict/batch",
                "Description": "Batch predictions",
            },
            {"Method": "POST", "Endpoint": "/predict/csv", "Description": "CSV upload"},
            {
                "Method": "GET",
                "Endpoint": "/metrics",
                "Description": "Prometheus metrics",
            },
            {"Method": "GET", "Endpoint": "/docs", "Description": "API documentation"},
        ]

        st.dataframe(endpoints, width="stretch", hide_index=True)

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: gray; padding: 1rem;">'
    "🚌 Bus Passenger Classifier Dashboard | Built with Streamlit | "
    f'Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    "</div>",
    unsafe_allow_html=True,
)
