"""
Check MLflow for Random Forest Results
"""

import os
import glob

print("=" * 80)
print("CHECKING MLFLOW FOR RANDOM FOREST RESULTS")
print("=" * 80)

# Check MLflow directory
mlruns_path = "mlruns"

if os.path.exists(mlruns_path):
    print(f"\n✓ MLflow directory found: {mlruns_path}")
    
    # List experiments
    experiments = [d for d in os.listdir(mlruns_path) if os.path.isdir(os.path.join(mlruns_path, d)) and d != ".trash"]
    print(f"\n📂 Found {len(experiments)} experiments:")
    
    for exp_id in experiments:
        exp_path = os.path.join(mlruns_path, exp_id)
        meta_file = os.path.join(exp_path, "meta.yaml")
        
        if os.path.exists(meta_file):
            # Read experiment name
            with open(meta_file, 'r') as f:
                content = f.read()
                if 'name:' in content:
                    name = content.split('name:')[1].split('\n')[0].strip()
                    print(f"\n  Experiment ID {exp_id}: {name}")
                    
                    # Check for runs
                    runs_path = exp_path
                    run_dirs = [d for d in os.listdir(runs_path) 
                               if os.path.isdir(os.path.join(runs_path, d)) 
                               and d not in ['meta.yaml', '.trash']]
                    
                    print(f"    • {len(run_dirs)} runs")
                    
                    # Check if this is supervised learning experiment
                    if 'supervised' in name.lower():
                        print(f"    🎯 FOUND SUPERVISED LEARNING EXPERIMENT!")
                        
                        # Look for recent runs
                        for run_id in run_dirs[-3:]:  # Last 3 runs
                            run_path = os.path.join(runs_path, run_id)
                            metrics_path = os.path.join(run_path, "metrics")
                            
                            if os.path.exists(metrics_path):
                                print(f"\n      Run: {run_id[:8]}...")
                                
                                # Read metrics
                                metric_files = os.listdir(metrics_path)
                                for metric_file in metric_files:
                                    with open(os.path.join(metrics_path, metric_file), 'r') as f:
                                        lines = f.readlines()
                                        if lines:
                                            last_line = lines[-1]
                                            parts = last_line.strip().split()
                                            if len(parts) >= 2:
                                                value = float(parts[1])
                                                print(f"        • {metric_file}: {value:.4f}")
else:
    print(f"\n❌ MLflow directory not found: {mlruns_path}")
    print("\nMLflow runs are typically stored in:")
    print("  • mlruns/ directory")
    print("  • Or custom path specified in MLflow tracking URI")

# Check for saved model
print("\n" + "=" * 80)
print("CHECKING FOR SAVED MODEL FILE")
print("=" * 80)

model_path = "models/supervised/random_forest_model.pkl"
if os.path.exists(model_path):
    print(f"\n✓ Model file found: {model_path}")
    size = os.path.getsize(model_path) / (1024 * 1024)  # MB
    print(f"  Size: {size:.2f} MB")
    print(f"  Modified: {os.path.getmtime(model_path)}")
else:
    print(f"\n❌ Model file not found: {model_path}")
    print("\nThe model should have been saved when you ran:")
    print("  python train_supervised.py random_forest")

print("\n" + "=" * 80)
print("HOW TO VIEW RESULTS")
print("=" * 80)

print("\n1. Open MLflow UI in browser:")
print("   http://localhost:5000")

print("\n2. Look for experiment named:")
print("   'supervised_learning_random_forest'")

print("\n3. Click on the experiment to see all runs")

print("\n4. Click on a run to see:")
print("   • Metrics (accuracy, F1-score)")
print("   • Parameters (model settings)")
print("   • Artifacts (saved model)")
print("   • Classification report")

print("\n" + "=" * 80)
