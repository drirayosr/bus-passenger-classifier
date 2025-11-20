"""
Start MLflow UI server
Run this to view experiment results in your browser
"""

import subprocess
import sys

def start_mlflow_ui(host='127.0.0.1', port=5000):
    """
    Start MLflow UI server
    
    Args:
        host: Host address (default: 127.0.0.1)
        port: Port number (default: 5000)
    """
    print("=" * 60)
    print("Starting MLflow UI Server")
    print("=" * 60)
    print(f"\nServer will start at: http://{host}:{port}")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    try:
        subprocess.run([
            sys.executable, "-m", "mlflow", "ui",
            "--host", host,
            "--port", str(port)
        ])
    except KeyboardInterrupt:
        print("\n\nMLflow UI server stopped.")

if __name__ == "__main__":
    start_mlflow_ui()
