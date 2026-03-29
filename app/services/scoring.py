from __future__ import annotations
import math
from typing import Optional
from app.models.schemas import (
    MeteorologicalInput,
    GeographicInput,
    LogisticInput,
    EnvironmentalInput,
    MeteorologicalBreakdown,
    GeographicBreakdown,
    LogisticBreakdown,
    EnvironmentalBreakdown,
    SafetyOverride,
)

WIND_SPEED_HARD_LIMIT_KNOTS: float = 30.0
LIGHTNING_HARD_LIMIT_PERCENT: float = 20.0
EQUATORIAL_VELOCITY_MS: float = 465.0  # m/s at equator

def evaluate_safety_override(met: MeteorologicalInput) -> SafetyOverride:
    if met.wind_speed_knots > WIND_SPEED_HARD_LIMIT_KNOTS:
        return SafetyOverride(
            triggered=True,
            reason=f"Rüzgar hızı {met.wind_speed_knots:.1f} knot, {WIND_SPEED_HARD_LIMIT_KNOTS} knot sınırını aştı.",
        )
    if met.lightning_probability_percent > LIGHTNING_HARD_LIMIT_PERCENT:
        return SafetyOverride(
            triggered=True,
            reason=f"Yıldırım olasılığı %{met.lightning_probability_percent:.1f}, %{LIGHTNING_HARD_LIMIT_PERCENT} sınırını aştı.",
        )
    return SafetyOverride(triggered=False)


# ─── Meteorological Score ─────────────────────────────────────────────────────

def _wind_score(wind_speed_knots: float) -> float:
    """
    0 knot'ta 100'den başlayarak sert sınırda 0'a kadar ters doğrusal azalma.
    Sınırın ötesinde puan 0'da sabitlenir.
    """
    score = max(0.0, 100.0 * (1.0 - wind_speed_knots / WIND_SPEED_HARD_LIMIT_KNOTS))
    return round(score, 4)


def _humidity_score(humidity: float) -> float:
    """
    Optimal fırlatma nemi %30–60 arasıdır. 45% merkezli Gauss çan eğrisi kullanılır.
    """
    optimal_center = 45.0
    sigma = 25.0
    score = 100.0 * math.exp(-0.5 * ((humidity - optimal_center) / sigma) ** 2)
    return round(score, 4)


def _cloud_score(cloud_coverage: float) -> float:
    """Doğrusal azalma: %0'da 100, %100 örtüde 0."""
    return round(max(0.0, 100.0 - cloud_coverage), 4)


def _lightning_penalty(lightning_prob: float) -> float:
    """
    Üstel ceza. Eşiğin altında ceza küçüktür. Üzerinde hızla çöker.
    """
    penalty = 100.0 * math.exp(-0.08 * lightning_prob)
    return round(penalty, 4)


def _temperature_score(temp_celsius: float) -> float:
    """
    Optimal aralık 10–35°C. 22.5°C merkezli Gauss çan eğrisi.
    Aşırı soğuk (<-20) veya aşırı sıcak (>50) diskalifiye edici bölgedir.
    """
    optimal_center = 22.5
    sigma = 20.0
    score = 100.0 * math.exp(-0.5 * ((temp_celsius - optimal_center) / sigma) ** 2)
    return round(score, 4)


def score_meteorological(met: MeteorologicalInput) -> MeteorologicalBreakdown:
    ws = _wind_score(met.wind_speed_knots)
    hum = _humidity_score(met.humidity_percent)
    cloud = _cloud_score(met.cloud_coverage_percent)
    lightning = _lightning_penalty(met.lightning_probability_percent)
    temp = _temperature_score(met.temperature_celsius)

    # Weighted composite: wind is most critical
    composite = (
        0.30 * ws +
        0.15 * hum +
        0.20 * cloud +
        0.25 * lightning +
        0.10 * temp
    )

    return MeteorologicalBreakdown(
        raw_wind_score=ws,
        raw_humidity_score=hum,
        raw_cloud_score=cloud,
        raw_lightning_penalty=lightning,
        raw_temperature_score=temp,
        normalized_score=round(composite, 4),
    )


# ─── Geographic Score ─────────────────────────────────────────────────────────

def _rotational_velocity(latitude_deg: float) -> float:
    """v = 465 * cos(lat_rad) m/s cinsinden"""
    lat_rad = math.radians(abs(latitude_deg))
    return round(EQUATORIAL_VELOCITY_MS * math.cos(lat_rad), 4)


def _velocity_score(velocity_ms: float) -> float:
    """Ekvator maksimumuna (465 m/s) göre normalleştir."""
    return round(100.0 * velocity_ms / EQUATORIAL_VELOCITY_MS, 4)


def _safety_distance_score(distance_km: float) -> float:
    """
    Logaritmik büyüme: ~500 km sonrasında azalan getiriler.
    Puan 1000 km'de ~100'e ulaşır.
    """
    if distance_km <= 0:
        return 0.0
    score = min(100.0, 100.0 * math.log1p(distance_km) / math.log1p(1000.0))
    return round(score, 4)


def _elevation_score(elevation_m: float) -> float:
    """
    Yüksek irtifa = ince atmosfer = ~4000m'ye kadar hafif avantaj,
    sonrasında yapısal/lojistik zorluklar getiriyi azaltır.
    1500m merkezli çan eğrisi.
    """
    optimal = 1500.0
    sigma = 2000.0
    score = 100.0 * math.exp(-0.5 * ((elevation_m - optimal) / sigma) ** 2)
    return round(score, 4)


def score_geographic(geo: GeographicInput) -> GeographicBreakdown:
    velocity = _rotational_velocity(geo.latitude_deg)
    vel_score = _velocity_score(velocity)
    dist_score = _safety_distance_score(geo.distance_to_nearest_city_km)
    elev_score = _elevation_score(geo.elevation_m)

    composite = (
        0.40 * vel_score +
        0.40 * dist_score +
        0.20 * elev_score
    )

    return GeographicBreakdown(
        rotational_velocity_boost_ms=velocity,
        velocity_score=vel_score,
        safety_distance_score=dist_score,
        elevation_score=elev_score,
        normalized_score=round(composite, 4),
    )


# ─── Logistic Score ───────────────────────────────────────────────────────────

def score_logistic(log: LogisticInput) -> LogisticBreakdown:
    fuel = log.fuel_availability_percent
    infra = log.infrastructure_readiness_percent
    range_safety = 100.0 if log.range_safety_cleared else 0.0
    crew = log.crew_readiness_percent
    supply = log.supply_chain_index

    composite = (
        0.25 * fuel +
        0.20 * infra +
        0.25 * range_safety +
        0.15 * crew +
        0.15 * supply
    )

    return LogisticBreakdown(
        fuel_score=round(fuel, 4),
        infrastructure_score=round(infra, 4),
        range_safety_score=round(range_safety, 4),
        crew_score=round(crew, 4),
        supply_chain_score=round(supply, 4),
        normalized_score=round(composite, 4),
    )


# ─── Environmental Score ──────────────────────────────────────────────────────

def _noise_score(noise_db: float) -> float:
    """
    Gürültü seviyesi 140 dB'de maksimum risk, 70 dB'de güvenli.
    Gauss eğrisi ile optimal aralık (75–85 dB) maksimize edilir.
    """
    optimal_center = 80.0
    sigma = 30.0
    score = 100.0 * math.exp(-0.5 * ((noise_db - optimal_center) / sigma) ** 2)
    return round(score, 4)


def _air_quality_score(air_quality_index: float) -> float:
    """
    Hava kalitesi endeksi 0–50 = iyi (100 puan)
    Endeks arttıkça puan logaritmik olarak azalır.
    500 endeksinde 0 puana yaklaşır.
    """
    if air_quality_index <= 0:
        return 100.0
    score = 100.0 / (1.0 + 0.2 * air_quality_index)
    return round(max(0.0, score), 4)


def _ecosystem_score(proximity_km: float) -> float:
    """
    Koruma alanına uzaklık arttıkça güvenliği artırır.
    100 km'de ~100 puan, 0 km'de 0 puan.
    """
    if proximity_km >= 500:
        return 100.0
    score = min(100.0, 100.0 * proximity_km / 500.0)
    return round(score, 4)


def _water_contamination_score(contamination_risk: float) -> float:
    """
    Su kirliliği riski düşük ise yüksek puan.
    Riski 100% ise 0 puan.
    """
    score = 100.0 - contamination_risk
    return round(max(0.0, score), 4)


def _carbon_footprint_score(carbon_kg: float) -> float:
    """
    Karbon ayak izi logaritmik olarak puana çevrilir.
    0 kg = 100 puan, 10000 kg = 0 puan.
    """
    if carbon_kg <= 0:
        return 100.0
    score = 100.0 - (100.0 * math.log1p(carbon_kg) / math.log1p(10000.0))
    return round(max(0.0, score), 4)


def score_environmental(env: EnvironmentalInput) -> EnvironmentalBreakdown:
    """
    Çevresel etki skorunu hesapla: gürültü, hava, ekosistem, su, karbon
    """
    noise = _noise_score(env.noise_level_db)
    air = _air_quality_score(env.air_quality_index)
    ecosystem = _ecosystem_score(env.ecosystem_proximity_km)
    water = _water_contamination_score(env.water_contamination_risk)
    carbon = _carbon_footprint_score(env.carbon_footprint_kg)

    # Ağırlıklı kompozisyon
    composite = (
        0.25 * noise +
        0.25 * air +
        0.25 * ecosystem +
        0.15 * water +
        0.10 * carbon
    )

    return EnvironmentalBreakdown(
        noise_score=noise,
        air_quality_score=air,
        ecosystem_score=ecosystem,
        water_contamination_score=water,
        carbon_footprint_score=carbon,
        normalized_score=round(composite, 4),
    )