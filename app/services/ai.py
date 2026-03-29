from __future__ import annotations
import csv
import random
from pathlib import Path
from typing import Iterable

from joblib import dump, load
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

from app.models.schemas import (
    LaunchSimulationRequest,
    MeteorologicalInput,
    GeographicInput,
    LogisticInput,
    EnvironmentalInput,
)
from app.services.simulation import run_simulation

DEFAULT_MODEL_PATH = Path("app/models/ai_model.joblib")
DEFAULT_DATASET_PATH = Path("synthetic_launch_dataset.csv")

FEATURE_NAMES = [
    "wind_speed_knots",
    "wind_direction_deg",
    "humidity_percent",
    "cloud_coverage_percent",
    "lightning_probability_percent",
    "temperature_celsius",
    "latitude_deg",
    "longitude_deg",
    "distance_to_nearest_city_km",
    "elevation_m",
    "fuel_availability_percent",
    "infrastructure_readiness_percent",
    "range_safety_cleared",
    "crew_readiness_percent",
    "supply_chain_index",
    "noise_level_db",
    "air_quality_index",
    "ecosystem_proximity_km",
    "water_contamination_risk",
    "carbon_footprint_kg",
]

STATUS_ORDER = ["NO-GO", "CONDITIONAL", "GO"]


def _sample_meteorological() -> MeteorologicalInput:
    return MeteorologicalInput(
        wind_speed_knots=round(random.uniform(0.0, 40.0), 2),
        wind_direction_deg=round(random.uniform(0.0, 360.0), 2),
        humidity_percent=round(random.uniform(10.0, 90.0), 2),
        cloud_coverage_percent=round(random.uniform(0.0, 100.0), 2),
        lightning_probability_percent=round(random.uniform(0.0, 40.0), 2),
        temperature_celsius=round(random.uniform(-20.0, 45.0), 2),
    )


def _sample_meteorological_go() -> MeteorologicalInput:
    """GO sınıfı için ideal meteorolojik koşullar üretir"""
    return MeteorologicalInput(
        wind_speed_knots=round(random.uniform(0.0, 15.0), 2),  # Düşük rüzgar
        wind_direction_deg=round(random.uniform(0.0, 360.0), 2),
        humidity_percent=round(random.uniform(30.0, 60.0), 2),  # Optimal nem
        cloud_coverage_percent=round(random.uniform(0.0, 20.0), 2),  # Açık gökyüzü
        lightning_probability_percent=round(random.uniform(0.0, 5.0), 2),  # Çok düşük yıldırım riski
        temperature_celsius=round(random.uniform(15.0, 30.0), 2),  # Optimal sıcaklık
    )


def _sample_geographic() -> GeographicInput:
    return GeographicInput(
        latitude_deg=round(random.uniform(-60.0, 60.0), 4),
        longitude_deg=round(random.uniform(-180.0, 180.0), 4),
        distance_to_nearest_city_km=round(random.uniform(0.0, 1000.0), 2),
        elevation_m=round(random.uniform(-200.0, 4500.0), 2),
    )


def _sample_geographic_go() -> GeographicInput:
    """GO sınıfı için ideal coğrafi koşullar üretir"""
    return GeographicInput(
        latitude_deg=round(random.uniform(-30.0, 30.0), 4),  # Ekvatora yakın
        longitude_deg=round(random.uniform(-180.0, 180.0), 4),
        distance_to_nearest_city_km=round(random.uniform(50.0, 500.0), 2),  # Güvenli mesafe
        elevation_m=round(random.uniform(0.0, 2000.0), 2),  # Uygun yükseklik
    )


def _sample_logistic() -> LogisticInput:
    return LogisticInput(
        fuel_availability_percent=round(random.uniform(30.0, 100.0), 2),
        infrastructure_readiness_percent=round(random.uniform(20.0, 100.0), 2),
        range_safety_cleared=random.choice([True, False]),
        crew_readiness_percent=round(random.uniform(30.0, 100.0), 2),
        supply_chain_index=round(random.uniform(20.0, 100.0), 2),
    )


def _sample_logistic_go() -> LogisticInput:
    """GO sınıfı için ideal lojistik koşullar üretir"""
    return LogisticInput(
        fuel_availability_percent=round(random.uniform(90.0, 100.0), 2),  # Yüksek yakıt
        infrastructure_readiness_percent=round(random.uniform(90.0, 100.0), 2),  # Tam altyapı
        range_safety_cleared=True,  # Güvenlik onaylı
        crew_readiness_percent=round(random.uniform(90.0, 100.0), 2),  # Hazır mürettebat
        supply_chain_index=round(random.uniform(90.0, 100.0), 2),  # Mükemmel tedarik
    )


def _sample_environmental() -> EnvironmentalInput:
    return EnvironmentalInput(
        noise_level_db=round(random.uniform(60.0, 160.0), 2),
        air_quality_index=round(random.uniform(5.0, 250.0), 2),
        ecosystem_proximity_km=round(random.uniform(0.0, 800.0), 2),
        water_contamination_risk=round(random.uniform(0.0, 70.0), 2),
        carbon_footprint_kg=round(random.uniform(200.0, 4500.0), 2),
    )


def _sample_environmental_go() -> EnvironmentalInput:
    """GO sınıfı için ideal çevresel koşullar üretir"""
    return EnvironmentalInput(
        noise_level_db=round(random.uniform(60.0, 120.0), 2),  # Kontrollü gürültü
        air_quality_index=round(random.uniform(5.0, 50.0), 2),  # Temiz hava
        ecosystem_proximity_km=round(random.uniform(100.0, 800.0), 2),  # Güvenli mesafe
        water_contamination_risk=round(random.uniform(0.0, 10.0), 2),  # Düşük risk
        carbon_footprint_kg=round(random.uniform(200.0, 1500.0), 2),  # Düşük karbon
    )


def _flatten_request(request: LaunchSimulationRequest) -> dict[str, float | int]:
    return {
        "wind_speed_knots": request.meteorological.wind_speed_knots,
        "wind_direction_deg": request.meteorological.wind_direction_deg,
        "humidity_percent": request.meteorological.humidity_percent,
        "cloud_coverage_percent": request.meteorological.cloud_coverage_percent,
        "lightning_probability_percent": request.meteorological.lightning_probability_percent,
        "temperature_celsius": request.meteorological.temperature_celsius,
        "latitude_deg": request.geographic.latitude_deg,
        "longitude_deg": request.geographic.longitude_deg,
        "distance_to_nearest_city_km": request.geographic.distance_to_nearest_city_km,
        "elevation_m": request.geographic.elevation_m,
        "fuel_availability_percent": request.logistic.fuel_availability_percent,
        "infrastructure_readiness_percent": request.logistic.infrastructure_readiness_percent,
        "range_safety_cleared": int(request.logistic.range_safety_cleared),
        "crew_readiness_percent": request.logistic.crew_readiness_percent,
        "supply_chain_index": request.logistic.supply_chain_index,
        "noise_level_db": request.environmental.noise_level_db,
        "air_quality_index": request.environmental.air_quality_index,
        "ecosystem_proximity_km": request.environmental.ecosystem_proximity_km,
        "water_contamination_risk": request.environmental.water_contamination_risk,
        "carbon_footprint_kg": request.environmental.carbon_footprint_kg,
    }


def generate_synthetic_data(
    sample_count: int = 1000,
    output_path: Path = DEFAULT_DATASET_PATH,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = FEATURE_NAMES + ["launch_readiness_score", "status"]

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        # GO sınıfı için minimum örnek sayısı garanti et
        go_target = max(50, int(sample_count * 0.15))  # En az 50 veya %15
        go_count = 0

        for i in range(sample_count):
            # GO sınıfı için özel üretim stratejisi
            if go_count < go_target and (i < go_target or random.random() < 0.25):
                # GO koşullarında veri üret
                request = LaunchSimulationRequest(
                    meteorological=_sample_meteorological_go(),
                    geographic=_sample_geographic_go(),
                    logistic=_sample_logistic_go(),
                    environmental=_sample_environmental_go(),
                    site_name="SENTETIK_GO_TESIS",
                )
            else:
                # Normal rastgele veri üret
                request = LaunchSimulationRequest(
                    meteorological=_sample_meteorological(),
                    geographic=_sample_geographic(),
                    logistic=_sample_logistic(),
                    environmental=_sample_environmental(),
                    site_name="SENTETIK_TESIS",
                )

            result = run_simulation(request)

            # GO hedefini karşıladıysak say
            if result.status == "GO":
                go_count += 1

            row = _flatten_request(request)
            row["launch_readiness_score"] = result.launch_readiness_score
            row["status"] = result.status
            writer.writerow(row)

    return output_path


def _load_dataset(path: Path) -> tuple[list[list[float]], list[str]]:
    data = []
    labels = []
    with path.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            features = [float(row[name]) for name in FEATURE_NAMES]
            data.append(features)
            labels.append(row["status"])
    return data, labels


def train_ai_model(
    dataset_path: Path = DEFAULT_DATASET_PATH,
    model_path: Path = DEFAULT_MODEL_PATH,
    test_size: float = 0.2,
    random_state: int = 42,
) -> tuple[RandomForestClassifier, float, str]:
    X, y = _load_dataset(dataset_path)

    class_counts = {label: y.count(label) for label in set(y)}
    stratify_target = y
    if len(class_counts) < 2 or any(count < 2 for count in class_counts.values()):
        stratify_target = None

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify_target,
    )

    model = RandomForestClassifier(n_estimators=200, random_state=random_state, n_jobs=-1)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    available_labels = [label for label in STATUS_ORDER if label in set(y_test) or label in set(predictions)]
    report = classification_report(
        y_test,
        predictions,
        labels=available_labels,
        target_names=available_labels,
    )

    dump(model, model_path)
    return model, accuracy, report


def evaluate_ai_model(
    dataset_path: Path = DEFAULT_DATASET_PATH,
    model_path: Path = DEFAULT_MODEL_PATH,
) -> tuple[float, str, list]:
    from sklearn.metrics import confusion_matrix

    X, y = _load_dataset(dataset_path)
    model = load_ai_model(model_path)
    predictions = model.predict(X)
    accuracy = accuracy_score(y, predictions)
    report = classification_report(y, predictions, target_names=STATUS_ORDER)

    # Confusion matrix hesapla
    cm = confusion_matrix(y, predictions, labels=STATUS_ORDER)
    cm_list = cm.tolist()

    return accuracy, report, cm_list


def load_ai_model(model_path: Path = DEFAULT_MODEL_PATH) -> RandomForestClassifier:
    return load(model_path)


def predict_status(request: LaunchSimulationRequest, model_path: Path = DEFAULT_MODEL_PATH) -> str:
    model = load_ai_model(model_path)
    features = [list(_flatten_request(request).values())]
    prediction = model.predict(features)
    return str(prediction[0])
