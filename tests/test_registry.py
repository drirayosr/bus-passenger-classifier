"""
Quick test of Model Registry functionality
"""
import warnings
warnings.filterwarnings('ignore')

import mlflow
from src.model_registry import ModelRegistry

# Initialize registry
print("=" * 60)
print("Testing Model Registry")
print("=" * 60)

registry = ModelRegistry()

# Test 1: List experiments
print("\n[Test 1] Listing experiments...")
experiments = mlflow.search_experiments()
for exp in experiments:
    print(f"  - {exp.name} (ID: {exp.experiment_id})")

# Test 2: Get latest run
print("\n[Test 2] Getting latest run...")
latest_run = registry.get_latest_run("bus_passenger_classification")
if latest_run is not None:
    print(f"[OK] Found run: {latest_run['run_id']}")
    print(f"    F1 Score: {latest_run.get('metrics.f1_score', 'N/A')}")
    print(f"    Accuracy: {latest_run.get('metrics.accuracy', 'N/A')}")
else:
    print("[ERROR] No runs found")

# Test 3: List registered models
print("\n[Test 3] Listing registered models...")
registry.list_registered_models()

print("\n" + "=" * 60)
print("[OK] Model Registry tests complete")
print("=" * 60)
