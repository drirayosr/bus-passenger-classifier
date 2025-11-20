# Phase 2: MLflow Experiment Tracking

## ✅ What We've Set Up

1. **MLflow Integration** - Automatic tracking of all experiments
2. **Comprehensive Logging** - Parameters, metrics, models, and artifacts
3. **Experiment Scripts** - Easy to run multiple experiments

## 📂 Files Created

- `src/train_mlflow.py` - Training with MLflow tracking
- `src/run_experiments.py` - Run multiple experiments with different configs
- `start_mlflow_ui.py` - Start MLflow web UI

## 🚀 Quick Start

### 1. Train with MLflow Tracking
```bash
python -m src.train_mlflow
```

This will:
- Train the model with current config
- Log all hyperparameters
- Log all metrics (F1, accuracy, precision, recall, confusion matrix)
- Save the model and artifacts
- Create visualizations (confusion matrix heatmap)

### 2. View Results in MLflow UI
```bash
python start_mlflow_ui.py
```

Then open your browser to: **http://127.0.0.1:5000**

### 3. Run Multiple Experiments
```bash
python -m src.run_experiments
```

This will test 4 different configurations and log all results.

## 📊 What MLflow Tracks

### Parameters Logged:
- `aoi_buffer_m` - Area of interest buffer
- `speed_limit_kmh` - Maximum speed threshold
- `pca_n_components` - Number of PCA components
- `hdbscan_min_cluster_size` - HDBSCAN clustering parameter
- `hdbscan_cluster_selection_epsilon` - Epsilon parameter
- `hdbscan_cluster_selection_method` - Selection method (eom/leaf)

### Metrics Logged:
- `f1_score` - Overall F1 score
- `accuracy` - Overall accuracy
- `precision_weighted` - Weighted precision
- `recall_weighted` - Weighted recall
- `precision_out`, `recall_out`, `f1_out` - OUT class metrics
- `precision_in`, `recall_in`, `f1_in` - IN class metrics
- `true_positives`, `true_negatives`, `false_positives`, `false_negatives`
- `n_samples_evaluated` - Number of samples used
- `n_passengers_raw`, `n_bus_records`, `n_bus_stops` - Data statistics

### Artifacts Logged:
- Trained pipeline model
- Confusion matrix visualization (PNG)
- Results summary (joblib)

## 🔍 MLflow UI Features

1. **Compare Runs** - Side-by-side comparison of different experiments
2. **Visualizations** - Automatic plots of metrics over time
3. **Model Registry** - Version and manage your models
4. **Search & Filter** - Find specific experiments quickly
5. **Artifact Viewer** - View confusion matrices and other artifacts

## 💡 Tips

### Compare Different Configurations
1. Modify `config/config.yaml` with new parameters
2. Run `python -m src.train_mlflow`
3. Repeat with different configs
4. Compare in MLflow UI

### Find Best Model
Sort experiments by F1 score in the MLflow UI to find the best performing configuration.

### Tag Experiments
Experiments are automatically tagged with:
- `status`: success/failed
- `model_type`: hdbscan_clustering
- `feature_engineering`: speed_accel_bearing_distance

## 📈 Current Best Results

**Optimized Configuration:**
- F1 Score: **0.596**
- Accuracy: 52.0%
- min_cluster_size: 300
- cluster_selection_epsilon: 0.5

## 🔄 Next Steps

1. **More Experiments** - Try different PCA components, speed limits, etc.
2. **Feature Engineering** - Add time-based features, user patterns
3. **Cross-Validation** - Implement k-fold validation
4. **Model Registry** - Promote best models to production
5. **API Integration** - Serve models via REST API

## 🐛 Troubleshooting

### MLflow UI won't start
```bash
# Check if MLflow is installed
pip show mlflow

# If not, install it
pip install mlflow
```

### Can't see experiments
Make sure you're running the UI from the project root directory where `mlruns/` folder exists.

### Port already in use
```bash
# Use a different port
python -c "from start_mlflow_ui import start_mlflow_ui; start_mlflow_ui(port=5001)"
```

## 📚 MLflow Documentation
- [MLflow Tracking](https://mlflow.org/docs/latest/tracking.html)
- [MLflow Projects](https://mlflow.org/docs/latest/projects.html)
- [MLflow Models](https://mlflow.org/docs/latest/models.html)
