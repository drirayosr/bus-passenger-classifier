"""
API Client Examples
Example scripts for interacting with the API
"""
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    print("\n" + "=" * 60)
    print("Testing Health Endpoint")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_single_prediction():
    """Test single prediction"""
    print("\n" + "=" * 60)
    print("Testing Single Prediction (Raw Format)")
    print("=" * 60)
    
    # Use CSV column names directly
    payload = {
        "id": "128",
        "timestamp_utc": "2020-01-22T10:16:22.321000+00:00",
        "lat": 55.792232,
        "lon": 12.522917,
        "speed": 0.0
    }
    
    print("\nRequest:")
    print(json.dumps(payload, indent=2))
    
    response = requests.post(f"{BASE_URL}/predict/single", json=payload)
    print(f"\nStatus: {response.status_code}")
    print("\nResponse:")
    print(json.dumps(response.json(), indent=2))


def test_batch_prediction():
    """Test batch prediction"""
    print("\n" + "=" * 60)
    print("Testing Batch Prediction")
    print("=" * 60)
    
    # Use CSV column names directly
    payload = {
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
            },
            {
                "id": "128",
                "timestamp_utc": "2020-01-22T10:16:23.079000+00:00",
                "lat": 55.792243,
                "lon": 12.522934,
                "speed": 0.43
            }
        ]
    }
    
    print(f"\nRequest: {len(payload['data'])} data points")
    
    response = requests.post(f"{BASE_URL}/predict/batch", json=payload)
    print(f"\nStatus: {response.status_code}")
    print("\nResponse:")
    result = response.json()
    print(json.dumps({
        "summary": result.get("summary"),
        "model_info": result.get("model_info"),
        "predictions_count": len(result.get("predictions", []))
    }, indent=2))
    
    # Print first few predictions
    if "predictions" in result:
        print("\nFirst 3 predictions:")
        for pred in result["predictions"][:3]:
            print(f"  User: {pred['user_id']}, Label: {pred['predicted_label']}, Confidence: {pred.get('confidence', 'N/A')}")


def test_model_info():
    """Test model info endpoint"""
    print("\n" + "=" * 60)
    print("Testing Model Info")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/model/info")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(response.text)


def main():
    """Run all examples"""
    try:
        test_health()
        test_model_info()
        test_single_prediction()
        test_batch_prediction()
        
        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Could not connect to API")
        print("Make sure the API is running: python start_api.py")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
