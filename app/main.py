from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(
    title="Gökbörü: Akıllı Fırlatma Karar Sistemi",
    description=(
        "Meteorolojik, coğrafi, lojistik ve çevresel veriler kullanarak optimal "
        "roket fırlatma koşullarını belirlemek için simülasyon ve karar destek sistemi. "
        "Fırlatma Hazırlık Puanı ve GO/CONDITIONAL/NO-GO durumunu döndürür."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1", tags=["Launch Simulation"])


@app.get("/health", tags=["Sistem"])
def health_check() -> dict:
    return {"status": "çalışıyor", "system": "Gökbörü v1.0.0"}