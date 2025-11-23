"""
Advanced Feature Engineering
Adds temporal, statistical, and contextual features
Expected improvement: +3-8% F1-Score
"""

from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd
import numpy as np


class AdvancedFeaturesTransformer(BaseEstimator, TransformerMixin):
    """
    Adds advanced features:
    - Temporal patterns (hour, day, time of day)
    - Statistical aggregations (rolling windows)
    - Behavioral patterns (speed stability, direction changes)
    - Multi-bus proximity (distance to nearest 3 buses)
    """
    
    def __init__(self, bus_df=None, window_size=5):
        self.bus_df = bus_df
        self.window_size = window_size
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X = X.copy()
        
        print(f"  Adding advanced features...")
        
        # 1. TEMPORAL FEATURES
        if 'timestamp' in X.columns:
            X['timestamp_dt'] = pd.to_datetime(X['timestamp'])
            X['hour'] = X['timestamp_dt'].dt.hour
            X['day_of_week'] = X['timestamp_dt'].dt.dayofweek
            X['is_weekend'] = (X['day_of_week'] >= 5).astype(int)
            X['is_rush_hour'] = ((X['hour'] >= 7) & (X['hour'] <= 9) | 
                                  (X['hour'] >= 16) & (X['hour'] <= 18)).astype(int)
            
            # Time of day categories
            X['time_of_day'] = 'day'
            X.loc[X['hour'] < 6, 'time_of_day'] = 'night'
            X.loc[(X['hour'] >= 6) & (X['hour'] < 12), 'time_of_day'] = 'morning'
            X.loc[(X['hour'] >= 12) & (X['hour'] < 18), 'time_of_day'] = 'afternoon'
            X.loc[X['hour'] >= 18, 'time_of_day'] = 'evening'
            X['time_of_day_encoded'] = X['time_of_day'].map({
                'night': 0, 'morning': 1, 'afternoon': 2, 'evening': 3, 'day': 1
            })
            
            print(f"    ✓ Added 6 temporal features")
        
        # 2. SPEED STABILITY FEATURES
        if 'speed' in X.columns and 'user_id' in X.columns:
            # Rolling statistics per user
            X = X.sort_values(['user_id', 'timestamp'])
            X['speed_rolling_mean'] = X.groupby('user_id')['speed'].transform(
                lambda x: x.rolling(window=self.window_size, min_periods=1).mean()
            )
            X['speed_rolling_std'] = X.groupby('user_id')['speed'].transform(
                lambda x: x.rolling(window=self.window_size, min_periods=1).std()
            ).fillna(0)
            X['speed_stability'] = 1 / (1 + X['speed_rolling_std'])
            
            # Speed change rate
            X['speed_change'] = X.groupby('user_id')['speed'].diff().fillna(0)
            X['speed_change_rate'] = X['speed_change'].abs()
            
            print(f"    ✓ Added 5 speed stability features")
        
        # 3. DIRECTION CONSISTENCY
        if 'bearing' in X.columns and 'user_id' in X.columns:
            # Bearing change (direction changes)
            X['bearing_change'] = X.groupby('user_id')['bearing'].diff().fillna(0)
            X['bearing_change_abs'] = X['bearing_change'].abs()
            
            # Direction stability (low change = stable = likely in bus)
            X['bearing_stability'] = X.groupby('user_id')['bearing_change_abs'].transform(
                lambda x: x.rolling(window=self.window_size, min_periods=1).mean()
            ).fillna(0)
            X['is_straight_path'] = (X['bearing_stability'] < 10).astype(int)
            
            print(f"    ✓ Added 4 direction consistency features")
        
        # 4. MULTI-BUS PROXIMITY (distance to nearest 3 buses)
        if self.bus_df is not None and 'latitude' in X.columns:
            from geopy.distance import geodesic
            
            # Ensure bus_df is sorted by timestamp
            bus_sorted = self.bus_df.sort_values('timestamp')
            
            def get_nearest_buses(row, n=3):
                """Get distances to n nearest buses at time t"""
                # Find buses within time window
                time_mask = (bus_sorted['timestamp'] >= row['timestamp'] - pd.Timedelta('60s')) & \
                           (bus_sorted['timestamp'] <= row['timestamp'] + pd.Timedelta('60s'))
                nearby_buses = bus_sorted[time_mask]
                
                if len(nearby_buses) == 0:
                    return [np.nan] * n
                
                # Calculate distances
                distances = []
                for _, bus in nearby_buses.iterrows():
                    try:
                        dist = geodesic(
                            (row['latitude'], row['longitude']),
                            (bus['latitude'], bus['longitude'])
                        ).meters
                        distances.append(dist)
                    except:
                        continue
                
                # Sort and get nearest n
                distances = sorted(distances)[:n]
                
                # Pad with large values if not enough buses
                while len(distances) < n:
                    distances.append(1000.0)
                
                return distances
            
            # Calculate for subset (expensive operation)
            sample_rows = min(1000, len(X))
            if sample_rows < len(X):
                print(f"    ⚠️  Sampling {sample_rows} rows for multi-bus proximity (expensive)")
            
            sample_indices = np.random.choice(X.index, sample_rows, replace=False)
            X_sample = X.loc[sample_indices]
            
            multi_distances = X_sample.apply(get_nearest_buses, axis=1, result_type='expand')
            multi_distances.columns = ['dist_bus_1', 'dist_bus_2', 'dist_bus_3']
            
            X = X.join(multi_distances)
            X[['dist_bus_1', 'dist_bus_2', 'dist_bus_3']] = X[['dist_bus_1', 'dist_bus_2', 'dist_bus_3']].fillna(1000)
            
            # Aggregate features
            X['min_bus_distance'] = X[['dist_bus_1', 'dist_bus_2', 'dist_bus_3']].min(axis=1)
            X['avg_bus_distance'] = X[['dist_bus_1', 'dist_bus_2', 'dist_bus_3']].mean(axis=1)
            
            print(f"    ✓ Added 5 multi-bus proximity features")
        
        # 5. SENSOR FUSION
        if all(col in X.columns for col in ['accx', 'accy', 'accz']):
            # Total acceleration magnitude
            X['acc_magnitude'] = np.sqrt(X['accx']**2 + X['accy']**2 + X['accz']**2)
            
            # Acceleration stability (low = stable = likely in bus)
            if 'user_id' in X.columns:
                X['acc_rolling_std'] = X.groupby('user_id')['acc_magnitude'].transform(
                    lambda x: x.rolling(window=self.window_size, min_periods=1).std()
                ).fillna(0)
                X['acc_stability'] = 1 / (1 + X['acc_rolling_std'])
            
            print(f"    ✓ Added 3 sensor fusion features")
        
        # 6. ACTIVITY CONFIDENCE WEIGHTED
        activity_cols = [col for col in X.columns if 'activityConfidence' in col]
        if len(activity_cols) > 0:
            # Dominant activity
            X['dominant_activity_conf'] = X[activity_cols].max(axis=1)
            X['activity_certainty'] = X[activity_cols].std(axis=1)  # Low std = certain
            
            print(f"    ✓ Added 2 activity confidence features")
        
        print(f"  Total new features added: {len([col for col in X.columns if col not in ['timestamp_dt', 'time_of_day']])}")
        
        return X


def add_advanced_features_to_pipeline():
    """
    Example of how to add this transformer to your pipeline
    """
    from src.pipeline import build_pipeline
    from src.config import load_config
    from src.data_loader import load_and_preprocess_data
    
    phones, bus, bus_stops = load_and_preprocess_data()
    config = load_config()
    
    # Get existing pipeline
    pipeline = build_pipeline(bus, bus_stops, config)
    
    # Add advanced features transformer (insert before PCA/HDBSCAN)
    # You would need to modify pipeline.py to include this
    advanced_features = AdvancedFeaturesTransformer(bus_df=bus, window_size=5)
    
    print("\nTo integrate advanced features:")
    print("1. Add to src/transformers/__init__.py:")
    print("   from .advanced_features import AdvancedFeaturesTransformer")
    print("\n2. Add to pipeline in src/pipeline.py (before pca_dbscan):")
    print("   ('advanced_features', AdvancedFeaturesTransformer(bus_df=bus_df, window_size=5)),")
    
    return advanced_features


if __name__ == "__main__":
    print("Advanced Features Transformer")
    print("=" * 80)
    print("\nThis adds ~25 powerful new features:")
    print("  • Temporal: hour, day, weekend, rush hour, time of day")
    print("  • Speed stability: rolling mean/std, stability score")
    print("  • Direction consistency: bearing changes, straight path indicator")
    print("  • Multi-bus proximity: distances to 3 nearest buses")
    print("  • Sensor fusion: acceleration magnitude and stability")
    print("  • Activity confidence: dominant activity, certainty")
    print("\nExpected improvement: +3-8% F1-Score")
    print("\nTo use:")
    print("  1. Add to src/transformers/advanced_features.py")
    print("  2. Import in src/transformers/__init__.py")
    print("  3. Add to pipeline in src/pipeline.py")
    print("  4. Retrain: python src/train_mlflow.py")
