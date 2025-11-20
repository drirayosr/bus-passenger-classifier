"""
API Tests
Test the FastAPI endpoints
"""
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

import pytest
import requests
import time
from typing import Generator

# API base URL
BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="module")
def api_client() -> Generator:
    """Ensure API is running before tests"""
    # Try to connect
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print(f"\n[OK] API is running at {BASE_URL}")
                break
        except requests.exceptions.RequestException:
            if i < max_retries - 1:
                print(f"[INFO] Waiting for API... (attempt {i+1}/{max_retries})")
                time.sleep(2)
            else:
                pytest.skip("API is not running. Start it with: python start_api.py")
    
    yield BASE_URL


class TestHealthEndpoints:
    """Test health and info endpoints"""
    
    def test_root_endpoint(self, api_client):
        """Test root endpoint"""
        response = requests.get(f"{api_client}/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_check(self, api_client):
        """Test health check endpoint"""
        response = requests.get(f"{api_client}/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "model_loaded" in data
        assert data["status"] in ["healthy", "degraded"]
    
    def test_model_info(self, api_client):
        """Test model info endpoint"""
        response = requests.get(f"{api_client}/model/info")
        
        # May return 503 if no model loaded
        if response.status_code == 200:
            data = response.json()
            assert "model_name" in data
            assert "version" in data
            assert "stage" in data


class TestPredictionEndpoints:
    """Test prediction endpoints"""
    
    def test_single_prediction(self, api_client):
        """Test single prediction endpoint"""
        payload = {
            "user_id": "test_user_123",
            "timestamp": "2020-01-23T12:34:56Z",
            "latitude": 55.8,
            "longitude": 12.52,
            "speed": 1.5
        }
        
        response = requests.post(f"{api_client}/predict/single", json=payload)
        
        # May return 503 if no model loaded
        if response.status_code == 200:
            data = response.json()
            assert "user_id" in data
            assert "predicted_label" in data
            assert data["predicted_label"] in [0, 1]
            assert "model_info" in data
        elif response.status_code == 503:
            pytest.skip("No model loaded in API")
    
    def test_batch_prediction(self, api_client):
        """Test batch prediction endpoint"""
        payload = {
            "data": [
                {
                    "user_id": "user_1",
                    "timestamp": "2020-01-23T12:34:56Z",
                    "latitude": 55.8,
                    "longitude": 12.52,
                    "speed": 1.5
                },
                {
                    "user_id": "user_1",
                    "timestamp": "2020-01-23T12:35:01Z",
                    "latitude": 55.80001,
                    "longitude": 12.52001,
                    "speed": 1.6
                }
            ]
        }
        
        response = requests.post(f"{api_client}/predict/batch", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            assert "predictions" in data
            assert "summary" in data
            assert "model_info" in data
            assert len(data["predictions"]) == 2
            assert data["summary"]["total_predictions"] == 2
        elif response.status_code == 503:
            pytest.skip("No model loaded in API")
    
    def test_invalid_coordinates(self, api_client):
        """Test validation with invalid coordinates"""
        payload = {
            "user_id": "test_user",
            "timestamp": "2020-01-23T12:34:56Z",
            "latitude": 200,  # Invalid
            "longitude": 12.52,
            "speed": 1.5
        }
        
        response = requests.post(f"{api_client}/predict/single", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_missing_required_fields(self, api_client):
        """Test validation with missing fields"""
        payload = {
            "user_id": "test_user",
            "timestamp": "2020-01-23T12:34:56Z"
            # Missing latitude and longitude
        }
        
        response = requests.post(f"{api_client}/predict/single", json=payload)
        assert response.status_code == 422  # Validation error


class TestDocumentation:
    """Test API documentation"""
    
    def test_openapi_schema(self, api_client):
        """Test OpenAPI schema is available"""
        response = requests.get(f"{api_client}/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data
    
    def test_swagger_ui(self, api_client):
        """Test Swagger UI is accessible"""
        response = requests.get(f"{api_client}/docs")
        assert response.status_code == 200
        assert "swagger" in response.text.lower() or "openapi" in response.text.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
