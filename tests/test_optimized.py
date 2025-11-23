"""
Test Optimized Configuration
Quick test of the improved hyperparameters
"""

import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("TESTING OPTIMIZED CONFIGURATION")
print("=" * 80)

print("\n📊 Loading and training with optimized settings...")
print("\nOptimized hyperparameters:")
print("  • PCA components: 4 → 5")
print("  • min_cluster_size: 300 → 180")
print("  • min_samples: auto → 12")
print("  • cluster_selection_epsilon: 0.5 → 0.35")
print("  • AOI buffer: 50m → 75m")
print("  • Speed limit: 35 km/h → 40 km/h")
print("  • Time tolerance: 60s → 90s")

print("\n" + "-" * 80)
print("Training model (this may take 2-3 minutes)...")
print("-" * 80)

# Run training with optimized config
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "src/train_mlflow.py"],
    capture_output=True,
    text=True
)

# Display output
print(result.stdout)

if result.returncode == 0:
    print("\n" + "=" * 80)
    print("✓ TRAINING COMPLETE!")
    print("=" * 80)
    print("\nCheck MLflow UI for detailed results:")
    print("  http://localhost:5000")
    print("\nLook for improvements in:")
    print("  • F1-Score (target: >65%)")
    print("  • Accuracy (target: >70%)")
    print("  • Precision & Recall balance")
else:
    print("\n" + "=" * 80)
    print("❌ ERROR DURING TRAINING")
    print("=" * 80)
    print(result.stderr)

print("\n" + "=" * 80)
print("NEXT STEPS")
print("=" * 80)
print("\n1. View results in MLflow: http://localhost:5000")
print("2. Compare with previous runs")
print("3. If improvement is good, config is already saved")
print("4. If not satisfied, run: python quick_improve.py")
print("   (tests 6 different configurations)")
