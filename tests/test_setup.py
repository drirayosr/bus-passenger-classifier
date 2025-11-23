"""
Test script to verify all modules are working correctly
Run this after installation to check everything is set up properly
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

print("=" * 60)
print("Testing Bus Passenger Classification Pipeline")
print("=" * 60)

# Test 1: Import core libraries
print("\n[1/7] Testing core libraries...")
try:
    import pandas as pd
    import numpy as np
    import sklearn
    print("✓ pandas, numpy, scikit-learn imported successfully")
except ImportError as e:
    print(f"✗ Failed to import core libraries: {e}")
    sys.exit(1)

# Test 2: Import HDBSCAN
print("\n[2/7] Testing HDBSCAN...")
try:
    import hdbscan
    print("✓ HDBSCAN imported successfully")
except ImportError as e:
    print(f"✗ Failed to import HDBSCAN: {e}")
    print("  Install with: pip install hdbscan")
    sys.exit(1)

# Test 3: Import geopy
print("\n[3/7] Testing geopy...")
try:
    import geopy
    print("✓ geopy imported successfully")
except ImportError as e:
    print(f"✗ Failed to import geopy: {e}")
    sys.exit(1)

# Test 4: Load configuration
print("\n[4/7] Testing configuration loader...")
try:
    from src.config import load_config
    config = load_config('config/config.yaml')
    print(f"✓ Configuration loaded successfully")
    print(f"  - AOI buffer: {config['preprocessing']['aoi_buffer_m']}m")
    print(f"  - Speed limit: {config['preprocessing']['speed_limit_kmh']} km/h")
except Exception as e:
    print(f"✗ Failed to load configuration: {e}")
    sys.exit(1)

# Test 5: Test utility functions
print("\n[5/7] Testing utility functions...")
try:
    from src.utils import haversine_array, to_utc, detect_column
    
    # Test haversine
    dist = haversine_array(55.7922, 12.5230, 55.7923, 12.5231)
    print(f"✓ Haversine distance calculation works: {dist:.2f} meters")
    
    # Test column detection
    test_df = pd.DataFrame({'lat': [1, 2], 'lon': [3, 4]})
    col = detect_column(test_df, ['latitude', 'lat', 'Lat'])
    print(f"✓ Column detection works: found '{col}'")
except Exception as e:
    print(f"✗ Failed to test utilities: {e}")
    sys.exit(1)

# Test 6: Test transformers
print("\n[6/7] Testing transformers...")
try:
    from src.transformers import (
        SpeedTransformer,
        AccelerationTransformer,
        BearingRateVariationTransformer
    )
    
    # Create sample data
    sample_data = pd.DataFrame({
        'user_id': [1, 1, 1],
        'lat': [55.7922, 55.7923, 55.7924],
        'lon': [12.5230, 12.5231, 12.5232],
        'timestamp_utc': pd.to_datetime([
            '2020-01-22 10:00:00',
            '2020-01-22 10:00:10',
            '2020-01-22 10:00:20'
        ], utc=True)
    })
    
    # Test SpeedTransformer
    speed_transformer = SpeedTransformer(speed_limit_mps=20.0)
    result = speed_transformer.fit_transform(sample_data)
    print(f"✓ SpeedTransformer works: computed {len(result)} speed values")
    
    # Test AccelerationTransformer
    accel_transformer = AccelerationTransformer()
    result = accel_transformer.fit_transform(result)
    print(f"✓ AccelerationTransformer works")
    
    # Test BearingTransformer
    bearing_transformer = BearingRateVariationTransformer()
    result = bearing_transformer.fit_transform(result)
    print(f"✓ BearingRateVariationTransformer works")
    
except Exception as e:
    print(f"✗ Failed to test transformers: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 7: Check data directory
print("\n[7/7] Checking data directory...")
data_dir = project_root / 'data' / 'raw'
if data_dir.exists():
    csv_files = list(data_dir.glob('*.csv'))
    if csv_files:
        print(f"✓ Data directory exists with {len(csv_files)} CSV files")
        for f in csv_files:
            print(f"  - {f.name}")
    else:
        print(f"⚠ Data directory exists but no CSV files found")
        print(f"  Please copy bus.csv and passengers.csv to: {data_dir}")
else:
    print(f"⚠ Data directory not found at: {data_dir}")

# Summary
print("\n" + "=" * 60)
print("✓ All tests passed! Pipeline is ready to use.")
print("=" * 60)
print("\nNext steps:")
print("1. Copy bus.csv and passengers.csv to data/raw/")
print("2. Run: python src/config.py")
print("3. Ready to build the full pipeline!")
print()
