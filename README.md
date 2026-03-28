# 🇹🇷 Gökbörü: Akıllı Fırlatma Karar Sistemi
<<<<<<< HEAD
=======

Bu proje, Türkçe yerelleştirilmiş bir füze fırlatma karar destek sistemi için prototip bir backend ve frontend içerir. AI hazır hale gelmesi için sentetik veri üretimi ve model eğitimi desteklenmiştir.

## Kurulum

1. Sanal ortam oluşturun:
>>>>>>> 4e15dd194cd2b3b029f6db32e7eb691c62ea5628

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Bağımlılıkları yükleyin:

```bash
pip install -r app/requirements.txt
```

## Çalıştırma

Backend:

```bash
uvicorn app.main:app --reload
```

Frontend:

```bash
streamlit run app/streamlit_app.py
```

## AI Entegrasyonu

- `POST /api/v1/ai-predict`: aynı girişlerle AI modelinden GO/CONDITIONAL/NO-GO tahmini alır.
- `GET /api/v1/ai/metrics`: modelin doğruluk ve sınıflandırma raporunu döndürür.

Streamlit arayüzü, model eğitilmişse AI tahminini ve model performansını de ekranda gösterir.

## AI Prototip ve Eğitim

Projeye yapay zeka eklemek için sentetik veri üretip bir model eğitebilirsiniz:

```bash
python train_ai.py --samples 2000
```

Bu komut, `synthetic_launch_dataset.csv` ve `app/models/ai_model.joblib` dosyalarını oluşturur.

