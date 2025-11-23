"""
Deploy Prefect Workflows with Schedules
Run this to set up automated workflows
"""

from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule, IntervalSchedule
from workflows import train_model_flow, batch_predictions_flow, model_monitoring_flow
from datetime import timedelta

# ============= DEPLOYMENT 1: Weekly Training =============
training_deployment = Deployment.build_from_flow(
    flow=train_model_flow,
    name="weekly-model-training",
    version="1.0",
    description="Trains the model every Sunday at 2 AM",
    schedule=CronSchedule(
        cron="0 2 * * 0",  # Every Sunday at 2:00 AM
        timezone="Europe/Copenhagen"
    ),
    tags=["training", "ml", "weekly"]
)

# ============= DEPLOYMENT 2: Daily Predictions =============
predictions_deployment = Deployment.build_from_flow(
    flow=batch_predictions_flow,
    name="daily-batch-predictions",
    version="1.0",
    description="Runs batch predictions every day at 8 AM",
    schedule=CronSchedule(
        cron="0 8 * * *",  # Every day at 8:00 AM
        timezone="Europe/Copenhagen"
    ),
    tags=["prediction", "daily"]
)

# ============= DEPLOYMENT 3: Regular Monitoring =============
monitoring_deployment = Deployment.build_from_flow(
    flow=model_monitoring_flow,
    name="model-monitoring",
    version="1.0",
    description="Monitors model performance every 6 hours",
    schedule=IntervalSchedule(
        interval=timedelta(hours=6)  # Every 6 hours
    ),
    tags=["monitoring", "drift-detection"]
)


def deploy_all():
    """Deploy all workflows"""
    print("🚀 Deploying Prefect Workflows...")
    
    print("\n1️⃣ Deploying Weekly Training Flow...")
    training_deployment.apply()
    print("   ✅ weekly-model-training deployed (Sundays at 2 AM)")
    
    print("\n2️⃣ Deploying Daily Predictions Flow...")
    predictions_deployment.apply()
    print("   ✅ daily-batch-predictions deployed (Daily at 8 AM)")
    
    print("\n3️⃣ Deploying Monitoring Flow...")
    monitoring_deployment.apply()
    print("   ✅ model-monitoring deployed (Every 6 hours)")
    
    print("\n" + "="*60)
    print("✅ All workflows deployed successfully!")
    print("="*60)
    
    print("\n📋 Next Steps:")
    print("   1. Start Prefect server: prefect server start")
    print("   2. View UI: http://localhost:4200")
    print("   3. Workflows will run automatically on schedule")
    print("\n💡 Manual execution:")
    print("   - Train: python workflows.py train")
    print("   - Predict: python workflows.py predict")
    print("   - Monitor: python workflows.py monitor")


if __name__ == "__main__":
    deploy_all()
