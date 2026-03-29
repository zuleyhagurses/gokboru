from __future__ import annotations
from typing import Optional
from app.models.schemas import (
    LaunchSimulationRequest,
    LaunchSimulationResult,
    ScoringWeights,
)
from app.services.scoring import (
    evaluate_safety_override,
    score_meteorological,
    score_geographic,
    score_logistic,
    score_environmental,
)


def _status_from_score(score: float) -> str:
    if score >= 75.0:
        return "GO"
    elif score >= 50.0:
        return "CONDITIONAL"
    else:
        return "NO-GO"


def _build_recommendation(status: str, score: float, override: bool, override_reason: Optional[str]) -> str:
    if override:
        return f"⛔ HAYIR: Güvenlik önlemselliği tetiklendi. {override_reason} Fırlatma dizisini hemen iptal edin."
    if status == "GO":
        return (
            f"✅ EVET FIRLATABİLİR: Tüm sistemler nominal. "
            f"Fırlatma Hazırlık Puanı {score:.2f}/100. "
            f"Son geri sayım dizisine devam edin."
        )
    elif status == "CONDITIONAL":
        return (
            f"⚠️ KOŞULLU EVET: {score:.2f}/100 puanı sınırda koşulları gösteriyor. "
            f"Misyon komutanları alt puanları gözden geçirmeli ve tanımlanan riskleri azaltmalıdır."
        )
    else:
        return (
            f"🔴 HAYIR: {score:.2f}/100 puanı kabul edilebilir eşiğin altındadır. "
            f"Meteorolojik ve lojistik koşulları yeniden değerlendirin. Fırlatma penceresini yeniden planlayın."
        )


def run_simulation(request: LaunchSimulationRequest) -> LaunchSimulationResult:
    override = evaluate_safety_override(request.meteorological)

    # Step 2: Domain scores
    met_breakdown = score_meteorological(request.meteorological)
    geo_breakdown = score_geographic(request.geographic)
    log_breakdown = score_logistic(request.logistic)
    env_breakdown = score_environmental(request.environmental)

    w: ScoringWeights = request.weights

    # Step 3: Composite score (now with environmental: 15%)
    # Ağırlıklar güncellendi: Meteoroloji: 0.34, Coğrafi: 0.26, Lojistik: 0.25, Çevre: 0.15
    composite_score = (
        0.34 * met_breakdown.normalized_score +
        0.26 * geo_breakdown.normalized_score +
        0.25 * log_breakdown.normalized_score +
        0.15 * env_breakdown.normalized_score
    )
    composite_score = round(composite_score, 4)

    # Step 4: Determine status (override collapses to NO-GO)
    if override.triggered:
        final_status = "NO-GO"
        final_score = 0.0
    else:
        final_status = _status_from_score(composite_score)
        final_score = composite_score

    recommendation = _build_recommendation(
        final_status, final_score, override.triggered, override.reason
    )

    return LaunchSimulationResult(
        site_name=request.site_name,
        launch_readiness_score=final_score,
        status=final_status,
        safety_override=override,
        meteorological_breakdown=met_breakdown,
        geographic_breakdown=geo_breakdown,
        logistic_breakdown=log_breakdown,
        environmental_breakdown=env_breakdown,
        weights_used=w,
        recommendation=recommendation,
    )