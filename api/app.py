"""
FastAPI Application
REST API for bus passenger classification predictions
"""
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
import io
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from api.schemas import (
    BatchPredictionRequest, BatchPredictionResponse,
    SinglePredictionRequest, SinglePredictionResponse,
    HealthResponse, ModelInfoResponse, ErrorResponse,
    PredictionResult
)
from src.model_registry import ModelRegistry
from src.config import load_config

# Initialize FastAPI app
app = FastAPI(
    title="Bus Passenger Classification API",
    description="Real-time predictions for bus passenger IN/OUT classification using GPS data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model and config
model = None
model_info = {}
config = None

# Metrics tracking
metrics = {
    "predictions_total": 0,
    "predictions_single": 0,
    "predictions_batch": 0,
    "predictions_csv": 0,
    "errors_total": 0,
    "api_calls_total": 0
}


def prepare_input_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare input data with all required columns for the pipeline
    
    Args:
        df: DataFrame with at least lat, lon, timestamp_utc
        
    Returns:
        DataFrame with all required columns
    """
    # Make a copy to avoid modifying original
    df = df.copy()
    
    # Ensure timestamp is datetime
    if 'timestamp_utc' in df.columns:
        df['timestamp_utc'] = pd.to_datetime(df['timestamp_utc'], utc=True)
    
    # Add id and user_id if missing - these are critical!
    if 'id' not in df.columns:
        if 'user_id' in df.columns:
            df['id'] = df['user_id']
        else:
            df['id'] = range(len(df))
    
    if 'user_id' not in df.columns:
        if 'id' in df.columns:
            df['user_id'] = df['id']
        else:
            df['user_id'] = range(len(df))
    
    # Sensor and beacon columns (fill with NaN if missing)
    sensor_cols = ['accx', 'accy', 'accz', 'rotx', 'roty', 'rotz', 
                   'magx', 'magy', 'magz', 'stationary', 'walking', 'running', 
                   'automotive', 'cycling', 'unknown', 'confidence',
                   'x_web', 'y_web', 'rssiA', 'rssiB', 'rssiC', 'rssi1', 'rssi2', 
                   'proxA', 'proxB', 'proxC', 'prox1', 'prox2', 'labelEnc', 'labelEnc2']
    
    for col in sensor_cols:
        if col not in df.columns:
            df[col] = np.nan
    
    # Ensure speed column exists
    if 'speed' not in df.columns:
        df['speed'] = np.nan
    
    return df


@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    global model, model_info, config
    
    print("=" * 60)
    print("Starting Bus Passenger Classification API")
    print("=" * 60)
    
    try:
        # Load configuration
        config = load_config()
        print("[OK] Configuration loaded")
        
        # Load production model
        registry = ModelRegistry()
        model = registry.load_production_model("bus-passenger-classifier")
        
        if model is None:
            print("[WARNING] No production model found! API will run in limited mode.")
            model_info = {
                "model_name": "bus-passenger-classifier",
                "version": "N/A",
                "stage": "None",
                "status": "NOT_LOADED"
            }
        else:
            # Get model info
            model_version = registry.get_model_info("bus-passenger-classifier", stage="Production")
            
            if model_version:
                model_info = {
                    "model_name": model_version.name,
                    "version": str(model_version.version),
                    "stage": model_version.current_stage,
                    "status": model_version.status,
                    "run_id": model_version.run_id
                }
                print(f"[OK] Production model loaded: v{model_info['version']}")
            else:
                model_info = {
                    "model_name": "bus-passenger-classifier",
                    "version": "Unknown",
                    "stage": "Production",
                    "status": "LOADED"
                }
                print("[OK] Model loaded (info unavailable)")
        
        print("=" * 60)
        print(f"API ready at http://localhost:8000")
        print(f"Docs at http://localhost:8000/docs")
        print("=" * 60)
        
    except Exception as e:
        print(f"[ERROR] Startup failed: {e}")
        import traceback
        traceback.print_exc()


@app.get("/", tags=["General"])
async def root():
    """Root endpoint"""
    return {
        "message": "Bus Passenger Classification API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint"""
    metrics["api_calls_total"] += 1
    return HealthResponse(
        status="healthy" if model is not None else "degraded",
        timestamp=datetime.utcnow().isoformat(),
        model_loaded=model is not None,
        model_info=model_info if model is not None else None
    )


@app.get("/model/info", response_model=ModelInfoResponse, tags=["Model"])
async def get_model_info():
    """Get information about the current model"""
    metrics["api_calls_total"] += 1
    if model is None:
        raise HTTPException(status_code=503, detail="No model loaded")
    
    return ModelInfoResponse(**model_info)


@app.get("/metrics", response_class=PlainTextResponse, tags=["Monitoring"])
async def get_metrics():
    """
    Prometheus-compatible metrics endpoint
    
    Returns basic metrics in Prometheus text format
    """
    lines = [
        "# HELP predictions_total Total number of predictions made",
        "# TYPE predictions_total counter",
        f"predictions_total {metrics['predictions_total']}",
        "",
        "# HELP predictions_single Total single predictions",
        "# TYPE predictions_single counter",
        f"predictions_single {metrics['predictions_single']}",
        "",
        "# HELP predictions_batch Total batch predictions",
        "# TYPE predictions_batch counter",
        f"predictions_batch {metrics['predictions_batch']}",
        "",
        "# HELP predictions_csv Total CSV predictions",
        "# TYPE predictions_csv counter",
        f"predictions_csv {metrics['predictions_csv']}",
        "",
        "# HELP errors_total Total number of errors",
        "# TYPE errors_total counter",
        f"errors_total {metrics['errors_total']}",
        "",
        "# HELP api_calls_total Total API calls",
        "# TYPE api_calls_total counter",
        f"api_calls_total {metrics['api_calls_total']}",
        "",
        "# HELP model_loaded Whether model is loaded (1=yes, 0=no)",
        "# TYPE model_loaded gauge",
        f"model_loaded {1 if model is not None else 0}",
    ]
    return "\n".join(lines)


@app.post("/predict/single", response_model=SinglePredictionResponse, tags=["Predictions"])
async def predict_single(request: SinglePredictionRequest):
    """
    Make a prediction for a single GPS data point
    
    - **user_id**: User identifier
    - **timestamp**: Timestamp in ISO format
    - **latitude**: Latitude in degrees
    - **longitude**: Longitude in degrees
    - **speed**: Optional speed in m/s
    """
    metrics["api_calls_total"] += 1
    metrics["predictions_single"] += 1
    
    if model is None:
        metrics["errors_total"] += 1
        raise HTTPException(status_code=503, detail="No model loaded")
    
    try:
        # Convert to DataFrame - using CSV column names directly
        data = pd.DataFrame([{
            'id': request.id,
            'user_id': request.id,
            'timestamp_utc': request.timestamp_utc,
            'lat': request.lat,
            'lon': request.lon,
            'speed': request.speed if request.speed is not None else np.nan
        }])
        
        # Prepare data with all required columns
        data = prepare_input_data(data)
        
        # Make prediction
        result = model.transform(data)
        
        if 'pca_dbscan_cluster' not in result.columns:
            metrics["errors_total"] += 1
            raise HTTPException(status_code=500, detail="Model output missing expected columns")
        
        prediction = int(result['pca_dbscan_cluster'].iloc[0])
        metrics["predictions_total"] += 1
        
        # Calculate confidence (using PCA distance)
        pca_cols = [c for c in result.columns if c.startswith('pca_component_')]
        if pca_cols:
            confidence = float(np.linalg.norm(result[pca_cols].iloc[0].values))
        else:
            confidence = None
        
        return SinglePredictionResponse(
            user_id=request.id,
            predicted_label=prediction,
            confidence=confidence,
            model_info=model_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        metrics["errors_total"] += 1
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/raw", tags=["Predictions"])
async def predict_raw(data: Dict[str, Any]):
    """
    Make a prediction with raw data format (accepts any column names)
    
    Accepts data in the same format as the training CSV:
    - id or user_id
    - lat, lon (or latitude, longitude)
    - timestamp_utc (or timestamp)
    - speed (optional)
    - All other columns are optional
    """
    metrics["api_calls_total"] += 1
    metrics["predictions_single"] += 1
    
    if model is None:
        metrics["errors_total"] += 1
        raise HTTPException(status_code=503, detail="No model loaded")
    
    try:
        # Convert to DataFrame directly from raw data
        df = pd.DataFrame([data])
        
        # Standardize column names if needed
        if 'latitude' in df.columns and 'lat' not in df.columns:
            df['lat'] = df['latitude']
        if 'longitude' in df.columns and 'lon' not in df.columns:
            df['lon'] = df['longitude']
        if 'timestamp' in df.columns and 'timestamp_utc' not in df.columns:
            df['timestamp_utc'] = df['timestamp']
        
        # Prepare data with all required columns
        df = prepare_input_data(df)
        
        # Make prediction
        result = model.transform(df)
        
        if 'pca_dbscan_cluster' not in result.columns:
            metrics["errors_total"] += 1
            raise HTTPException(status_code=500, detail="Model output missing expected columns")
        
        prediction = int(result['pca_dbscan_cluster'].iloc[0])
        metrics["predictions_total"] += 1
        
        # Calculate confidence
        pca_cols = [c for c in result.columns if c.startswith('pca_component_')]
        if pca_cols:
            confidence = float(np.linalg.norm(result[pca_cols].iloc[0].values))
        else:
            confidence = None
        
        user_id = data.get('id') or data.get('user_id', 'unknown')
        
        return {
            "user_id": str(user_id),
            "predicted_label": prediction,
            "confidence": confidence,
            "model_info": model_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        metrics["errors_total"] += 1
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/batch", response_model=BatchPredictionResponse, tags=["Predictions"])
async def predict_batch(request: BatchPredictionRequest):
    """
    Make predictions for a batch of GPS data points
    
    Processes multiple GPS points and returns predictions for each.
    """
    metrics["api_calls_total"] += 1
    
    if model is None:
        metrics["errors_total"] += 1
        raise HTTPException(status_code=503, detail="No model loaded")
    
    try:
        # Convert to DataFrame - using CSV column names directly
        data = pd.DataFrame([
            {
                'id': point.id,
                'user_id': point.id,
                'timestamp_utc': point.timestamp_utc,
                'lat': point.lat,
                'lon': point.lon,
                'speed': point.speed if point.speed is not None else np.nan
            }
            for point in request.data
        ])
        
        # Prepare data with all required columns
        data = prepare_input_data(data)
        
        # Make predictions
        result = model.transform(data)
        
        if 'pca_dbscan_cluster' not in result.columns:
            metrics["errors_total"] += 1
            raise HTTPException(status_code=500, detail="Model output missing expected columns")
        
        # Extract predictions
        predictions = []
        pca_cols = [c for c in result.columns if c.startswith('pca_component_')]
        
        for idx, row in result.iterrows():
            pred = PredictionResult(
                user_id=data.loc[idx, 'user_id'],
                predicted_label=int(row['pca_dbscan_cluster']),
                confidence=float(np.linalg.norm(row[pca_cols].values)) if pca_cols else None
            )
            predictions.append(pred)
        
        # Update metrics
        count = len(predictions)
        metrics["predictions_batch"] += 1
        metrics["predictions_total"] += count
        
        # Calculate summary
        pred_values = [p.predicted_label for p in predictions]
        unique, counts = np.unique(pred_values, return_counts=True)
        class_dist = {str(int(k)): int(v) for k, v in zip(unique, counts)}
        
        summary = {
            "total_predictions": len(predictions),
            "class_distribution": class_dist,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return BatchPredictionResponse(
            predictions=predictions,
            summary=summary,
            model_info=model_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        metrics["errors_total"] += 1
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")


@app.post("/predict/csv", tags=["Predictions"])
async def predict_from_csv(file: UploadFile = File(...)):
    """
    Upload a CSV file and get predictions
    
    CSV should have columns: user_id, timestamp, latitude, longitude
    Optional: speed
    """
    metrics["api_calls_total"] += 1
    
    if model is None:
        metrics["errors_total"] += 1
        raise HTTPException(status_code=503, detail="No model loaded")
    
    try:
        # Read CSV
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        # Handle flexible column names but keep CSV format
        if 'latitude' in df.columns and 'lat' not in df.columns:
            df['lat'] = df['latitude']
        if 'longitude' in df.columns and 'lon' not in df.columns:
            df['lon'] = df['longitude']
        if 'timestamp' in df.columns and 'timestamp_utc' not in df.columns:
            df['timestamp_utc'] = df['timestamp']
        
        # Validate required columns (after renaming)
        required_cols = ['lat', 'lon']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            metrics["errors_total"] += 1
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {missing_cols}. CSV must have 'lat' and 'lon' (or 'latitude' and 'longitude')"
            )
        
        # Ensure id column exists
        if 'id' not in df.columns:
            if 'user_id' in df.columns:
                df['id'] = df['user_id']
            else:
                df['id'] = range(len(df))
        
        # Prepare data with all required columns
        df = prepare_input_data(df)
        
        # Make predictions
        result = model.transform(df)
        
        if 'pca_dbscan_cluster' not in result.columns:
            metrics["errors_total"] += 1
            raise HTTPException(status_code=500, detail="Model output missing expected columns")
        
        # Update metrics
        count = len(result)
        metrics["predictions_csv"] += 1
        metrics["predictions_total"] += count
        
        # Return as CSV
        output = result[['pca_dbscan_cluster']].copy()
        output.columns = ['predicted_label']
        
        # Add user_id if available
        if 'user_id' in df.columns:
            output.insert(0, 'user_id', df['user_id'].iloc[result.index].values)
        elif 'id' in df.columns:
            output.insert(0, 'user_id', df['id'].iloc[result.index].values)
        
        csv_string = output.to_csv(index=False)
        
        return JSONResponse(
            content={
                "predictions_csv": csv_string,
                "summary": {
                    "total_predictions": len(output),
                    "class_distribution": output['predicted_label'].value_counts().to_dict()
                },
                "model_info": model_info
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        metrics["errors_total"] += 1
        raise HTTPException(status_code=500, detail=f"CSV prediction failed: {str(e)}")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    metrics["errors_total"] += 1
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            detail=str(exc),
            timestamp=datetime.utcnow().isoformat()
        ).dict()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
