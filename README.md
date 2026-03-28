# 🚀 Gökbörü: Akıllı Fırlatma Karar Sistemi

## Setup
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc:       http://localhost:8000/redoc

## Sample Request
```bash
curl -X POST http://localhost:8000/api/v1/simulate-launch \
  -H "Content-Type: application/json" \
  -d '{
    "site_name": "Cape Canaveral LC-39A",
    "meteorological": {
      "wind_speed_knots": 12.5,
      "wind_direction_deg": 270,
      "humidity_percent": 55,
      "cloud_coverage_percent": 20,
      "lightning_probability_percent": 5,
      "temperature_celsius": 24
    },
    "geographic": {
      "latitude_deg": 28.5,
      "longitude_deg": -80.6,
      "distance_to_nearest_city_km": 65,
      "elevation_m": 3
    },
    "logistic": {
      "fuel_availability_percent": 98,
      "infrastructure_readiness_percent": 95,
      "range_safety_cleared": true,
      "crew_readiness_percent": 92,
      "supply_chain_index": 88
    },
    "weights": {
      "meteorological": 0.40,
      "geographic": 0.30,
      "logistic": 0.30
    }
  }'
```
