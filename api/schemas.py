"""
API Schemas
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime


class GPSPoint(BaseModel):
    """Single GPS data point for prediction"""
    id: str = Field(..., description="User/passenger identifier")
    timestamp_utc: str = Field(..., description="Timestamp in ISO format with UTC")
    lat: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    lon: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    speed: Optional[float] = Field(None, description="Speed in m/s (optional)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "128",
                "timestamp_utc": "2020-01-22T10:16:22.321000+00:00",
                "lat": 55.792232,
                "lon": 12.522917,
                "speed": 0.0
            }
        }
    )


class BatchPredictionRequest(BaseModel):
    """Request for batch predictions"""
    data: List[GPSPoint] = Field(..., min_length=1, description="List of GPS data points")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": [
                    {
                        "id": "128",
                        "timestamp_utc": "2020-01-22T10:16:22.321000+00:00",
                        "lat": 55.792232,
                        "lon": 12.522917,
                        "speed": 0.0
                    },
                    {
                        "id": "128",
                        "timestamp_utc": "2020-01-22T10:16:22.325000+00:00",
                        "lat": 55.792244,
                        "lon": 12.522932,
                        "speed": 0.18
                    }
                ]
            }
        }
    )


class PredictionResult(BaseModel):
    """Single prediction result"""
    user_id: str
    predicted_label: int = Field(..., description="0 = OUT, 1 = IN")
    confidence: Optional[float] = Field(None, description="Confidence score")


class BatchPredictionResponse(BaseModel):
    """Response for batch predictions"""
    predictions: List[PredictionResult]
    summary: Dict[str, Any] = Field(
        ..., 
        description="Summary statistics"
    )
    model_info: Dict[str, Any] = Field(
        ...,
        description="Information about the model used"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "predictions": [
                    {"user_id": "user_123", "predicted_label": 1, "confidence": 0.85},
                    {"user_id": "user_123", "predicted_label": 0, "confidence": 0.92}
                ],
                "summary": {
                    "total_predictions": 2,
                    "class_distribution": {"0": 1, "1": 1}
                },
                "model_info": {
                    "model_name": "bus-passenger-classifier",
                    "version": "2",
                    "stage": "Production"
                }
            }
        }
    )


class SinglePredictionRequest(BaseModel):
    """Request for single prediction"""
    id: str
    timestamp_utc: str
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    speed: Optional[float] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "128",
                "timestamp_utc": "2020-01-22T10:16:22.321000+00:00",
                "lat": 55.792232,
                "lon": 12.522917,
                "speed": 0.0
            }
        }
    )


class SinglePredictionResponse(BaseModel):
    """Response for single prediction"""
    user_id: str
    predicted_label: int
    confidence: Optional[float] = None
    model_info: Dict[str, Any]


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    model_loaded: bool
    model_info: Optional[Dict[str, Any]] = None


class ModelInfoResponse(BaseModel):
    """Model information response"""
    model_name: str
    version: str
    stage: str
    status: str
    run_id: str
    metrics: Optional[Dict[str, float]] = None


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    timestamp: str
