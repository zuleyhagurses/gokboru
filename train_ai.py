#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import argparse

from app.services.ai import generate_synthetic_data, train_ai_model, DEFAULT_DATASET_PATH, DEFAULT_MODEL_PATH


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Synthetic dataset üretir ve RandomForest tabanlı AI modelini eğitir."
    )
    parser.add_argument("--samples", type=int, default=2000, help="Üretilecek örnek sayısı")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET_PATH,
        help="Oluşturulacak CSV dataset yolu",
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=DEFAULT_MODEL_PATH,
        help="Eğitilen modelin kaydedileceği yol",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    print("[1/2] Sentetik veri üretiliyor...")
    dataset_path = generate_synthetic_data(sample_count=args.samples, output_path=args.dataset)
    print(f"  Oluşturuldu: {dataset_path}")

    print("[2/2] AI modeli eğitiliyor...")
    model, accuracy, report = train_ai_model(dataset_path=dataset_path, model_path=args.model)

    print(f"Model kaydedildi: {args.model}")
    print(f"Test doğruluğu: {accuracy:.4f}")
    print("Sınıflandırma raporu:")
    print(report)


if __name__ == "__main__":
    main()
