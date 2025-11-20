"""
Data Validation Script
Run data quality checks before training
"""
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

import sys
import subprocess


def run_validation():
    """Run pytest data validation tests"""
    print("=" * 60)
    print("Running Data Validation Tests")
    print("=" * 60)
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_data_validation.py", "-v", "--tb=short"],
        capture_output=False
    )
    
    if result.returncode != 0:
        print("\n" + "=" * 60)
        print("[ERROR] Data validation failed!")
        print("Please fix data quality issues before training.")
        print("=" * 60)
        return False
    
    print("\n" + "=" * 60)
    print("[OK] All data validation tests passed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)
