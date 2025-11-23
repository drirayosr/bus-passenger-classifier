# Model Accuracy Improvement Guide

## Current Performance
- **Accuracy**: 68.2%
- **F1-Score**: 59.6%
- **Precision**: 59.8%
- **Recall**: 60.2%

## 🎯 Top Strategies to Improve Accuracy

### 1. **HDBSCAN Hyperparameter Tuning** (Most Impactful)

The clustering algorithm is the core of your model. Here are the key parameters to tune:

#### **min_cluster_size** (Currently: 300)
- **What it does**: Minimum points required to form a cluster
- **Impact**: Smaller = more granular clusters, larger = more stable clusters
- **Try**: `[100, 150, 200, 250, 300, 400, 500]`
- **Recommendation**: Start with **150-200** for better granularity

#### **min_samples** (Currently: None/auto)
- **What it does**: How conservative clustering is (higher = more conservative)
- **Impact**: Higher values create tighter, purer clusters
- **Try**: `[5, 10, 15, 20, 25]`
- **Recommendation**: Start with **10-15**

#### **cluster_selection_epsilon** (Currently: 0.5)
- **What it does**: Allows smaller clusters near large ones
- **Impact**: Lower = stricter separation, higher = more merging
- **Try**: `[0.0, 0.3, 0.5, 0.7, 1.0]`
- **Recommendation**: Try **0.3** for stricter clusters

#### **cluster_selection_method** (Currently: 'eom')
- **What it does**: How to select optimal clusters from hierarchy
- **Options**: 'eom' (Excess of Mass) or 'leaf' (leaf nodes)
- **Try both**: 'eom' tends to work better for mixed densities
- **Recommendation**: Keep **'eom'** or try **'leaf'**

### 2. **PCA Components Tuning**

Current: 4 components

**Try**: 3, 5, 6, 8 components
- Too few (2-3): May lose important information
- Too many (10+): May include noise
- **Optimal range**: 4-6 components for your 40+ features

### 3. **Feature Engineering Improvements**

#### Add New Features:
1. **Temporal features**:
   - Hour of day (rush hour patterns)
   - Day of week
   - Time since last bus stop

2. **Enhanced proximity**:
   - Distance to nearest 3 buses (not just 1)
   - Time-weighted distance (recent positions matter more)

3. **Behavioral patterns**:
   - Average speed over last 5 minutes
   - Speed variance (stable inside bus)
   - Bearing consistency

4. **Sensor fusion**:
   - Combined accelerometer + gyroscope features
   - Activity confidence weighted features

### 4. **Data Preprocessing Improvements**

#### Current Settings to Adjust:

1. **AOI Buffer** (Currently: 50m)
   - Try: 25m (stricter), 75m (looser), 100m (very loose)
   - **Recommendation**: **75m** to capture more context

2. **Speed Limit** (Currently: 35 km/h)
   - Try: 25 km/h, 30 km/h, 40 km/h, 50 km/h
   - **Recommendation**: **40 km/h** to include more valid data

3. **Time Tolerance** (Currently: 60s)
   - Try: 30s (stricter), 90s (looser), 120s (very loose)
   - **Recommendation**: **90s** for better bus matching

### 5. **Alternative Clustering Approaches**

Try different algorithms:

1. **GMM (Gaussian Mixture Models)**
   - Better for overlapping clusters
   - Provides probability scores

2. **OPTICS**
   - Similar to HDBSCAN but different density measure
   - Good for varied density data

3. **Ensemble approach**:
   - Train 3-5 models with different hyperparameters
   - Use voting or probability averaging

## 📊 Quick Testing Script

```python
# Test configurations quickly
test_configs = [
    # Baseline
    {'min_cluster_size': 300, 'min_samples': None, 'epsilon': 0.5},
    
    # More granular
    {'min_cluster_size': 150, 'min_samples': 10, 'epsilon': 0.3},
    
    # Tighter clusters
    {'min_cluster_size': 200, 'min_samples': 15, 'epsilon': 0.4},
    
    # Larger stable
    {'min_cluster_size': 400, 'min_samples': 20, 'epsilon': 0.6},
]
```

## 🛠️ Implementation Steps

### Option A: Manual Config Update (Fastest - 5 minutes)

1. **Edit `config/config.yaml`**:
```yaml
feature_engineering:
  pca_n_components: 5  # Try 5 instead of 4
  hdbscan_min_cluster_size: 150  # Reduce from 300
  hdbscan_min_samples: 10  # Set explicit value
  hdbscan_cluster_selection_epsilon: 0.3  # Reduce from 0.5
  hdbscan_cluster_selection_method: 'eom'  # Keep as is
```

2. **Retrain**:
```bash
python src/train_mlflow.py
```

3. **Check MLflow UI**: http://localhost:5000

### Option B: Automated Grid Search (Complete - 15-30 min)

```bash
# Install HDBSCAN if not installed
pip install hdbscan scikit-learn

# Run comprehensive grid search
python improve_accuracy.py

# Or run quick version (6 configs, ~5-10 min)
python quick_improve.py
```

### Option C: Manual Experimentation

Test one config at a time:

1. Update `config.yaml` with new parameters
2. Run: `python src/train_mlflow.py`
3. Check results in MLflow
4. Compare F1-scores
5. Iterate

## 📈 Expected Improvements

Based on typical HDBSCAN tuning:

| Change | Expected Improvement |
|--------|---------------------|
| Optimal min_cluster_size | +3-7% F1-score |
| Add min_samples | +2-4% F1-score |
| Optimal PCA components | +1-3% F1-score |
| Better preprocessing | +2-5% F1-score |
| **Combined** | **+8-15% F1-score** |

**Target**: 68% → **75-80% F1-score**

## 🎓 Recommended Configuration to Try First

```yaml
feature_engineering:
  # PCA
  pca_n_components: 5
  
  # HDBSCAN - Optimized for balance
  hdbscan_min_cluster_size: 180
  hdbscan_min_samples: 12
  hdbscan_cluster_selection_epsilon: 0.35
  hdbscan_cluster_selection_method: 'eom'

preprocessing:
  # Slightly relaxed constraints
  aoi_buffer_m: 75
  speed_limit_kmh: 40
  max_speed_mps: 11.11  # 40 km/h
  bus_time_tolerance: "90s"
```

This configuration:
- More granular clusters (180 vs 300)
- Explicit conservative clustering (min_samples=12)
- Stricter cluster separation (epsilon=0.35)
- More generous preprocessing (75m buffer, 40 km/h, 90s tolerance)

**Expected F1-Score**: 65-70% (up from 59.6%)

## 🔄 Iterative Improvement Process

1. **Week 1**: Tune HDBSCAN (biggest impact)
2. **Week 2**: Optimize PCA components
3. **Week 3**: Add new features
4. **Week 4**: Try ensemble methods

## 📝 Tracking Progress

All experiments automatically logged to MLflow:
- Compare runs visually
- Sort by F1-score
- Export best config
- Deploy best model automatically

## 🚀 Next Steps

1. **Immediate** (5 min): Update config with recommended settings above
2. **Short-term** (10 min): Run `quick_improve.py` to test 6 configs
3. **Medium-term** (30 min): Run full `improve_accuracy.py` grid search
4. **Long-term** (ongoing): Add new features and ensemble methods

---

**Questions?** Check MLflow experiments for detailed results: http://localhost:5000
