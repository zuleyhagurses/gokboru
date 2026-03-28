#!/usr/bin/env python3
"""Test script for environmental module integration"""

from app.models.schemas import (
    LaunchSimulationRequest,
    MeteorologicalInput,
    GeographicInput,
    LogisticInput,
    EnvironmentalInput,
)
from app.services.simulation import run_simulation

request = LaunchSimulationRequest(
    site_name="Test Tesisi",
    meteorological=MeteorologicalInput(
        wind_speed_knots=12.5,
        wind_direction_deg=270,
        humidity_percent=55,
        cloud_coverage_percent=20,
        lightning_probability_percent=5,
        temperature_celsius=24
    ),
    geographic=GeographicInput(
        latitude_deg=28.5,
        longitude_deg=-80.6,
        distance_to_nearest_city_km=65,
        elevation_m=3
    ),
    logistic=LogisticInput(
        fuel_availability_percent=98,
        infrastructure_readiness_percent=95,
        range_safety_cleared=True,
        crew_readiness_percent=92,
        supply_chain_index=88
    ),
    environmental=EnvironmentalInput(
        noise_level_db=140,
        air_quality_index=80,
        ecosystem_proximity_km=100,
        water_contamination_risk=15,
        carbon_footprint_kg=2500
    )
)

result = run_simulation(request)
print("✓ Simülasyon başarıyla tamamlandı!")
print(f"  Status: {result.status}")
print(f"  Hazırlık Puanı: {result.launch_readiness_score:.2f}")
print(f"  Meteoroloji: {result.meteorological_breakdown.normalized_score:.2f}")
print(f"  Coğrafi: {result.geographic_breakdown.normalized_score:.2f}")
print(f"  Lojistik: {result.logistic_breakdown.normalized_score:.2f}")
print(f"  Çevresel: {result.environmental_breakdown.normalized_score:.2f}")
print(f"\nÖneri: {result.recommendation}")
