"""
Quick test - Run this to verify installation
"""

print("Testing imports...")

try:
    import pandas as pd
    print("✓ pandas")
except:
    print("✗ pandas - run: pip install pandas")

try:
    import numpy as np
    print("✓ numpy")
except:
    print("✗ numpy - run: pip install numpy")

try:
    import sklearn
    print("✓ scikit-learn")
except:
    print("✗ scikit-learn - run: pip install scikit-learn")

try:
    import hdbscan
    print("✓ hdbscan")
except:
    print("✗ hdbscan - run: pip install hdbscan")

try:
    import geopy
    print("✓ geopy")
except:
    print("✗ geopy - run: pip install geopy")

try:
    import matplotlib
    print("✓ matplotlib")
except:
    print("✗ matplotlib - run: pip install matplotlib")

try:
    import yaml
    print("✓ pyyaml")
except:
    print("✗ pyyaml - run: pip install pyyaml")

print("\nAll good! Now test transformers with: python -m src.transformers.speed")
