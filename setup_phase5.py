"""
Phase 5 Setup and Demo
Complete workflow for Model Registry
"""
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("PHASE 5: MODEL REGISTRY - SETUP & DEMO")
print("=" * 70)

print("\n[Step 1] Checking MLflow setup...")
try:
    import mlflow
    from src.model_registry import ModelRegistry
    print("[OK] MLflow and Model Registry imported successfully")
except Exception as e:
    print(f"[ERROR] Import failed: {e}")
    print("Run: pip install mlflow")
    exit(1)

print("\n[Step 2] Checking for existing experiments...")
experiments = mlflow.search_experiments()
print(f"[OK] Found {len(experiments)} experiment(s):")
for exp in experiments:
    print(f"  - {exp.name} (ID: {exp.experiment_id})")

target_exp = "bus_passenger_classification"
has_target = any(exp.name == target_exp for exp in experiments)

if not has_target:
    print(f"\n[WARNING] Target experiment '{target_exp}' not found")
    print("\n[Action Required] Run training first:")
    print("  python -m src.train_mlflow")
    print("\nThis will:")
    print("  1. Create the experiment")
    print("  2. Train the model")
    print("  3. Log metrics and artifacts")
    print("  4. Enable model registration")
else:
    print(f"\n[OK] Target experiment '{target_exp}' exists!")
    
    print("\n[Step 3] Checking for runs...")
    registry = ModelRegistry()
    latest_run = registry.get_latest_run(target_exp)
    
    if latest_run is not None:
        print(f"[OK] Found latest run:")
        print(f"  Run ID: {latest_run['run_id']}")
        print(f"  F1 Score: {latest_run.get('metrics.f1_score', 'N/A')}")
        print(f"  Accuracy: {latest_run.get('metrics.accuracy', 'N/A')}")
        print(f"  Start Time: {latest_run['start_time']}")
        
        print("\n[Step 4] Checking registered models...")
        try:
            models = mlflow.search_registered_models()
            if len(models) == 0:
                print("[INFO] No models registered yet")
                print("\n[Action] Register this model:")
                print("  python -m src.model_registry --register")
            else:
                print(f"[OK] Found {len(models)} registered model(s):")
                for model in models:
                    print(f"  - {model.name}")
                    for version in model.latest_versions:
                        print(f"      Version {version.version}: {version.current_stage}")
        except Exception as e:
            print(f"[INFO] Model registry not accessible: {e}")
            print("[INFO] This is normal - models will be registered on first use")
        
        print("\n" + "=" * 70)
        print("NEXT STEPS:")
        print("=" * 70)
        print("\n1. Register the model:")
        print("   python -m src.model_registry --register")
        print("\n2. View in MLflow UI:")
        print("   python start_mlflow_ui.py")
        print("   Open: http://localhost:5000")
        print("\n3. Promote to Staging:")
        print("   python registry_manager.py --promote 1 --stage Staging")
        print("\n4. After testing, promote to Production:")
        print("   python registry_manager.py --promote 1 --stage Production")
        print("\n5. Use for predictions:")
        print("   python -m src.predict --stage Production --input data/test.csv")
    else:
        print("[INFO] No training runs found")
        print("\n[Action Required] Run training:")
        print("  python -m src.train_mlflow")

print("\n" + "=" * 70)
print("For full documentation, see: PHASE5_REGISTRY_GUIDE.md")
print("=" * 70)
