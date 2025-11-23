"""Test model prediction with minimal data"""
import pandas as pd
import numpy as np
import joblib
import sys
from pathlib import Path

# Add api to path
sys.path.append(str(Path(__file__).parent))

# Import prepare_input_data from api
from api.app import prepare_input_data

# Load model
print("Loading model...")
model = joblib.load('models/pipeline.joblib')
print(f"Model loaded: {type(model)}")
print(f"Pipeline steps: {[step[0] for step in model.steps]}")

# Create test data - exactly as API would send
test_data = pd.DataFrame([{
    'id': 'user_001',
    'user_id': 'user_001',
    'timestamp_utc': pd.Timestamp('2020-01-15 10:30:00', tz='UTC'),
    'lat': 55.7,
    'lon': 12.5,
    'speed': np.nan
}])

print("\nBEFORE prepare_input_data:")
print("Columns:", test_data.columns.tolist())
print("Shape:", test_data.shape)

# Prepare data (add all missing columns)
test_data = prepare_input_data(test_data)

print("\nAFTER prepare_input_data:")
print("Columns:", test_data.columns.tolist())
print("Shape:", test_data.shape)
print("\nDtypes:")
print(test_data.dtypes)

# Try prediction
try:
    print("\nRunning model.transform()...")
    result = model.transform(test_data)
    print("SUCCESS!")
    print("\nResult columns:", result.columns.tolist())
    print("Result shape:", result.shape)
    if 'pca_dbscan_cluster' in result.columns:
        print(f"Prediction: {result['pca_dbscan_cluster'].iloc[0]}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
