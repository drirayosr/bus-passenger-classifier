"""
Quick Start - Prefect Workflows
Run this to test your workflows immediately
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

def check_service(url, name):
    """Check if a service is running"""
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            print(f"✅ {name} is running")
            return True
    except:
        pass
    print(f"❌ {name} is NOT running")
    return False

def main():
    print("🚀 Prefect Workflow Quick Start")
    print("="*60)
    
    # Check prerequisites
    print("\n📋 Checking prerequisites...")
    api_running = check_service("http://localhost:8000/health", "FastAPI")
    mlflow_running = check_service("http://localhost:5000", "MLflow")
    
    if not api_running:
        print("\n⚠️  FastAPI is not running!")
        print("   Start it in another terminal: python start_api.py")
        return
    
    if not mlflow_running:
        print("\n⚠️  MLflow is not running!")
        print("   Start it in another terminal: python start_mlflow_ui.py")
        return
    
    print("\n✅ All services are ready!")
    
    # Check if Prefect is installed
    try:
        import prefect
        print(f"✅ Prefect {prefect.__version__} is installed")
    except ImportError:
        print("\n⚠️  Prefect is not installed!")
        print("   Installing now...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements/orchestration.txt"])
        print("✅ Prefect installed!")
    
    # Run test workflows
    print("\n" + "="*60)
    print("🧪 Running Test Workflows")
    print("="*60)
    
    workflows = [
        ("train", "Model Training"),
        ("predict", "Batch Predictions"),
        ("monitor", "Model Monitoring")
    ]
    
    for flow_arg, flow_name in workflows:
        print(f"\n🔄 Running {flow_name} Flow...")
        print("-"*60)
        result = subprocess.run(
            [sys.executable, "workflows.py", flow_arg],
            capture_output=False
        )
        if result.returncode == 0:
            print(f"✅ {flow_name} completed successfully!")
        else:
            print(f"❌ {flow_name} failed!")
        time.sleep(2)
    
    print("\n" + "="*60)
    print("✅ All test workflows completed!")
    print("="*60)
    
    print("\n📊 Next Steps:")
    print("   1. Start Prefect UI: prefect server start")
    print("   2. View at: http://localhost:4200")
    print("   3. Deploy scheduled workflows: python deploy_workflows.py")
    print("\n💡 Your workflows are ready for automatic scheduling!")

if __name__ == "__main__":
    main()
