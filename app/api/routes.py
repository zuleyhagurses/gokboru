from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    LaunchSimulationRequest,
    LaunchSimulationResult,
    HistoryResponse,
)
from app.services.simulation import run_simulation

router = APIRouter()

# In-memory store — keyed by simulation_id for O(1) dedup
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