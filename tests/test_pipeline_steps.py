"""Test to debug column order through pipeline"""
import pandas as pd
import numpy as np
import joblib

# Load model
model = joblib.load('models/pipeline.joblib')

# Minimal test data
test_data = pd.DataFrame([{
    'id': 123456,  # Use integer directly
    'user_id': 123456,  # Integer
    'timestamp_utc': pd.Timestamp('2020-01-15 10:30:00', tz='UTC'),
    'lat': 55.7,
    'lon': 12.5,
    'speed': np.nan,
    # Add all sensor columns
    'accx': np.nan, 'accy': np.nan, 'accz': np.nan,
    'rotx': np.nan, 'roty': np.nan, 'rotz': np.nan,
    'magx': np.nan, 'magy': np.nan, 'magz': np.nan,
    'stationary': np.nan, 'walking': np.nan, 'running': np.nan,
    'automotive': np.nan, 'cycling': np.nan, 'unknown': np.nan,
    'confidence': np.nan, 'x_web': np.nan, 'y_web': np.nan,
    'rssiA': np.nan, 'rssiB': np.nan, 'rssiC': np.nan,
    'rssi1': np.nan, 'rssi2': np.nan,
    'proxA': np.nan, 'proxB': np.nan, 'proxC': np.nan,
    'prox1': np.nan, 'prox2': np.nan,
    'labelEnc': np.nan, 'labelEnc2': np.nan
}])

print("Input columns:", test_data.columns.tolist())
print("Input dtypes:", test_data.dtypes.to_dict())

# Test each transformer step
current_data = test_data.copy()
for step_name, transformer in model.named_steps.items():
    print(f"\n{'='*60}")
    print(f"STEP: {step_name}")
    print(f"{'='*60}")
    try:
        current_data = transformer.transform(current_data)
        print(f"✓ Success")
        print(f"  Output shape: {current_data.shape}")
        print(f"  Output columns: {current_data.columns.tolist()}")
        num_cols = current_data.select_dtypes(include=np.number).columns.tolist()
        print(f"  Numerical columns ({len(num_cols)}): {num_cols}")
    except Exception as e:
        print(f"✗ FAILED: {e}")
        print(f"  Current columns: {current_data.columns.tolist()}")
        num_cols = current_data.select_dtypes(include=np.number).columns.tolist()
        print(f"  Numerical columns ({len(num_cols)}): {num_cols}")
        break
