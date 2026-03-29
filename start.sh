#!/bin/bash

# Gökbörü Proje Başlatma Scripti
echo "🇹🇷 Gökbörü Fırlatma Karar Destek Sistemi başlatılıyor..."

# Virtual environment'ı aktifleştir
source .venv/bin/activate

# Backend'i başlat (arka planda)
echo "🚀 Backend API başlatılıyor (port 8000)..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Kısa bekleme
sleep 2

# Frontend'i başlat (arka planda)
echo "🖥️  Frontend UI başlatılıyor (port 8501)..."
streamlit run app/streamlit_app.py --server.port 8501 --server.address 0.0.0.0 &
FRONTEND_PID=$!

echo ""
echo "✅ Servisler başlatıldı!"
echo "🌐 Web Arayüzü: http://localhost:8501"
echo "📚 API Dokümantasyonu: http://localhost:8000/docs"
echo ""
echo "🛑 Durdurmak için: Ctrl+C veya 'pkill -f uvicorn && pkill -f streamlit'"
echo ""
echo "PID'ler: Backend=$BACKEND_PID, Frontend=$FRONTEND_PID"

# Script'i çalışır tut
wait