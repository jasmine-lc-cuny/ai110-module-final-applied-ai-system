"""Simple reliability harness for the PawPal applied-AI layer."""

from __future__ import annotations

from pathlib import Path
import csv

from ai_system import advise_service
from constants import CATEGORY_TASK_TITLES


def main() -> None:
    grooming_titles = CATEGORY_TASK_TITLES["grooming"]
    advice = advise_service("grooming", "cat", grooming_titles)
    guides_path = Path(__file__).resolve().parent / "data" / "ai_guides.csv"
    guide_count = 0
    if guides_path.exists():
        with guides_path.open(newline="", encoding="utf-8") as handle:
            guide_count = sum(1 for _ in csv.DictReader(handle))
    print("Applied AI Evaluation")
    print("=====================")
    print("This harness checks the local advice layer and its integration points.")
    print(f"Retrieval guides loaded: {guide_count}")
    if advice is not None:
        print("PASS: Retrieval corpus available")
        print(f"PASS: Advice layer returned {advice.guide.category} guidance with confidence {advice.confidence:.2f}")
        print(f"PASS: Suggested defaults -> {', '.join(advice.guide.recommended_titles)}")
    else:
        print("FAIL: Retrieval corpus unavailable")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
