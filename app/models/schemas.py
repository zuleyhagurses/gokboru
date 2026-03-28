from __future__ import annotations
from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Literal, Optional
from datetime import datetime
import uuid


# ─── Input Schemas ────────────────────────────────────────────────────────────

class MeteorologicalInput(BaseModel):
    wind_speed_knots: float = Field(..., ge=0, le=150, description="Rüzgar hızı (knot cinsinden)")
    wind_direction_deg: float = Field(..., ge=0, le=360, description="Rüzgar yönü (derece cinsinden)")
    humidity_percent: float = Field(..., ge=0, le=100, description="Nispi nem (0–100%)")
    cloud_coverage_percent: float = Field(..., ge=0, le=100, description="Bulut örtüsü (0–100%)")
    lightning_probability_percent: float = Field(..., ge=0, le=100, description="Yıldırım olasılığı (0–100%)")
    temperature_celsius: float = Field(..., ge=-80, le=60, description="Ortam sıcaklığı (°C cinsinden)")


class GeographicInput(BaseModel):
    latitude_deg: float = Field(..., ge=-90, le=90, description="Fırlatma tesisi enlemi")
    longitude_deg: float = Field(..., ge=-180, le=180, description="Fırlatma tesisi boylamı")
    distance_to_nearest_city_km: float = Field(..., ge=0, description="En yakın yerleşim alanına uzaklık (km)")
    elevation_m: float = Field(..., ge=-500, le=9000, description="Deniz seviyesinden yükseklik (m)")


class LogisticInput(BaseModel):
    fuel_availability_percent: float = Field(..., ge=0, le=100, description="Yakıt kullanılabilirliği (0–100%)")
    infrastructure_readiness_percent: float = Field(..., ge=0, le=100, description="Altyapı hazırlığı (0–100%)")
    range_safety_cleared: bool = Field(..., description="Test alanı güvenlik onayı durumu")
    crew_readiness_percent: float = Field(..., ge=0, le=100, description="Mürettebat hazırlık puanı (0–100%)")
    supply_chain_index: float = Field(..., ge=0, le=100, description="Tedarik zinciri hazırlık endeksi (0–100%)")


class EnvironmentalInput(BaseModel):
    noise_level_db: float = Field(..., ge=0, le=200, description="Fırlatma gürültüsü seviyesi (dB)")
    air_quality_index: float = Field(..., ge=0, le=500, description="Hava kalitesi endeksi (0–500)")
    ecosystem_proximity_km: float = Field(..., ge=0, le=1000, description="Koruma alanına uzaklık (km)")
    water_contamination_risk: float = Field(..., ge=0, le=100, description="Su kirliliği riski (0–100%)")
    carbon_footprint_kg: float = Field(..., ge=0, le=10000, description="Karbon ayak izi (kg CO2)")


class ScoringWeights(BaseModel):
    meteorological: float = Field(default=0.40, ge=0, le=1)
    geographic: float = Field(default=0.30, ge=0, le=1)
    logistic: float = Field(default=0.30, ge=0, le=1)

    @model_validator(mode="after")
    def weights_must_sum_to_one(self) -> ScoringWeights:
        total = round(self.meteorological + self.geographic + self.logistic, 6)
        if abs(total - 1.0) > 1e-4:
            raise ValueError(f"Ağırlıklar toplamı 1.0 olmalıdır, toplam: {total}")
        return self


class LaunchSimulationRequest(BaseModel):
    meteorological: MeteorologicalInput
    geographic: GeographicInput
    logistic: LogisticInput
    environmental: EnvironmentalInput
    weights: ScoringWeights = Field(default_factory=ScoringWeights)
    site_name: str = Field(default="ADLANDIRILMAMIŞ_TESİS", max_length=64)


# ─── Output Schemas ───────────────────────────────────────────────────────────

class SafetyOverride(BaseModel):
    model_config = ConfigDict(json_schema_extra=None)
    triggered: bool
    reason: Optional[str] = None


class MeteorologicalBreakdown(BaseModel):
    raw_wind_score: float
    raw_humidity_score: float
    raw_cloud_score: float
    raw_lightning_penalty: float
    raw_temperature_score: float
    normalized_score: float  # 0–100


class GeographicBreakdown(BaseModel):
    rotational_velocity_boost_ms: float
    velocity_score: float
    safety_distance_score: float
    elevation_score: float
    normalized_score: float  # 0–100


class LogisticBreakdown(BaseModel):
    fuel_score: float
    infrastructure_score: float
    range_safety_score: float
    crew_score: float
    supply_chain_score: float
    normalized_score: float  # 0–100


class EnvironmentalBreakdown(BaseModel):
    noise_score: float
    air_quality_score: float
    ecosystem_score: float
    water_contamination_score: float
    carbon_footprint_score: float
    normalized_score: float  # 0–100


class LaunchSimulationResult(BaseModel):
    simulation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    site_name: str
    launch_readiness_score: float = Field(..., ge=0, le=100)
    status: Literal["GO", "CONDITIONAL", "NO-GO"]
    safety_override: SafetyOverride
    meteorological_breakdown: MeteorologicalBreakdown
    geographic_breakdown: GeographicBreakdown
    logistic_breakdown: LogisticBreakdown
    environmental_breakdown: EnvironmentalBreakdown
    weights_used: ScoringWeights
    recommendation: str


class HistoryResponse(BaseModel):
    total_simulations: int = Field(description="Toplam simülasyon sayısı")
    results: list[LaunchSimulationResult] = Field(description="Simülasyon sonuçları")


class AIPredictionResult(BaseModel):
    predicted_status: Literal["GO", "CONDITIONAL", "NO-GO"]
    ai_model_path: str = Field(description="Kullanılan AI model dosya yolu")
    note: Optional[str] = Field(default=None, description="AI tahminine ek bilgi")


class AIMetricsResponse(BaseModel):
    ai_model_path: str = Field(description="Eğitilmiş AI model dosya yolu")
    ai_dataset_path: str = Field(description="Değerlendirme için kullanılan dataset yolu")
    accuracy: float = Field(..., ge=0, le=1, description="Doğruluk skoru")
    report: str = Field(description="Sınıflandırma raporu")