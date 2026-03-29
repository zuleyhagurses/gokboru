from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    LaunchSimulationRequest,
    LaunchSimulationResult,
    HistoryResponse,
    AIPredictionResult,
    AIMetricsResponse,
)
from app.services.ai import (
    DEFAULT_DATASET_PATH,
    DEFAULT_MODEL_PATH,
    evaluate_ai_model,
    predict_status,
)
from app.services.simulation import run_simulation

router = APIRouter()

_simulation_history: dict[str, LaunchSimulationResult] = {}


@router.post(
    "/simulate-launch",
    response_model=LaunchSimulationResult,
    summary="Fırlatma hazırlık simülasyonu çalıştır",
    status_code=200,
)
def simulate_launch(request: LaunchSimulationRequest) -> LaunchSimulationResult:
    """
    Üç alan genelinde tam misyon girdilerini kabul eder ve
    Fırlatma Hazırlık Puanı ile tam alt-puan dökümleri döndürür.
    """
    try:
        result = run_simulation(request)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Simülasyon motoru hatası: {str(exc)}")

    _simulation_history[result.simulation_id] = result
    return result


@router.post(
    "/ai-predict",
    response_model=AIPredictionResult,
    summary="AI modeline göre fırlatma durumunu tahmin et",
    status_code=200,
)
def predict_launch_with_ai(request: LaunchSimulationRequest) -> AIPredictionResult:
    try:
        predicted_status = predict_status(request)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=(
                "AI modeli bulunamadı. Önce `python train_ai.py --samples 2000` ile model eğitin."
            ),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI tahmin hatası: {str(exc)}")

    return AIPredictionResult(
        predicted_status=predicted_status,
        ai_model_path=str(DEFAULT_MODEL_PATH),
        note="AI tabanlı tahmin sonucu",
    )


@router.get(
    "/ai/metrics",
    response_model=AIMetricsResponse,
    summary="Eğitilmiş modelin doğruluk ve performans raporunu getir",
)
def get_ai_metrics() -> AIMetricsResponse:
    try:
        accuracy, report, confusion_matrix = evaluate_ai_model()
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=(
                "AI modeli veya sentetik dataset bulunamadı. Önce `python train_ai.py --samples 2000` çalıştırın."
            ),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI değerlendirme hatası: {str(exc)}")

    return AIMetricsResponse(
        ai_model_path=str(DEFAULT_MODEL_PATH),
        ai_dataset_path=str(DEFAULT_DATASET_PATH),
        accuracy=accuracy,
        report=report,
        confusion_matrix=confusion_matrix,
    )


@router.get(
    "/history",
    response_model=HistoryResponse,
    summary="Tüm önceki simülasyon sonuçlarını al",
)
def get_history() -> HistoryResponse:
    """
    Geçerli sunucu oturumundan tüm simülasyon sonuçlarını döndürür,
    en yeni önce sıralanmış.
    """
    sorted_results = sorted(
        _simulation_history.values(),
        key=lambda r: r.timestamp,
        reverse=True,
    )
    return HistoryResponse(
        total_simulations=len(sorted_results),
        results=sorted_results,
    )