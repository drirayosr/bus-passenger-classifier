"""
Streamlit Dashboard Launcher
Run this script to start the dashboard
"""
import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    dashboard_path = Path(__file__).parent / "dashboard" / "app.py"
    
    print("=" * 60)
    print("🚌 Starting Bus Passenger Classifier Dashboard...")
    print("=" * 60)
    print(f"\n📂 Dashboard location: {dashboard_path}")
    print("\n🌐 Dashboard will open in your browser automatically")
    print("📡 Make sure the API is running on http://localhost:8000")
    print("\n🛑 Press Ctrl+C to stop the dashboard\n")
    print("=" * 60)
    
    # Start Streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        str(dashboard_path),
        "--server.port", "8501",
        "--server.headless", "false"
    ])
