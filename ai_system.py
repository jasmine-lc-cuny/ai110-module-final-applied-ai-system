"""Local retrieval-and-advice helpers for the applied-AI layer."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import csv
import json


@dataclass(frozen=True)
class CareGuide:
    category: str
    species: str
    keywords: tuple[str, ...]
    recommended_titles: tuple[str, ...]
    summary: str
    guardrail: str


@dataclass(frozen=True)
class CareAdvice:
    guide: CareGuide
    confidence: float
    explanation: str


def _load_guides(path: str | Path) -> list[CareGuide]:
    guides: list[CareGuide] = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            guides.append(
                CareGuide(
                    category=row["category"],
                    species=row["species"],
                    keywords=tuple(part.strip().lower() for part in row["keywords"].split(";") if part.strip()),
                    recommended_titles=tuple(part.strip() for part in row["recommended_titles"].split("|") if part.strip()),
                    summary=row["summary"],
                    guardrail=row["guardrail"],
                )
            )
    return guides


_GUIDES_PATH = Path(__file__).resolve().parent / "data" / "ai_guides.csv"
_GUIDES = _load_guides(_GUIDES_PATH) if _GUIDES_PATH.exists() else []
_LOG_PATH = Path(__file__).resolve().parent / "logs" / "ai_advice.jsonl"


def advise_service(category: str, species: str, title_options: list[str]) -> CareAdvice | None:
    """Return a small retrieval-backed recommendation for a service form."""
    if not _GUIDES:
        return None

    category_key = category.lower()
    species_key = species.lower()
    best = None
    best_score = -1.0
    for guide in _GUIDES:
        score = 0.0
        if guide.category == category_key:
            score += 2.0
        if guide.species == "all" or guide.species == species_key:
            score += 1.5
        score += sum(1.0 for keyword in guide.keywords if keyword in species_key or keyword in category_key)
        if score > best_score:
            best = guide
            best_score = score

    if best is None:
        return None

    recommended = [title for title in best.recommended_titles if title in title_options]
    if not recommended and title_options:
        recommended = [title_options[0]]

    confidence = min(0.95, 0.55 + best_score / 6)
    explanation = f"{best.summary} {best.guardrail}"
    advice = CareAdvice(best, round(confidence, 2), explanation)
    _log_advice(category, species, advice)
    return advice


def _log_advice(category: str, species: str, advice: CareAdvice) -> None:
    _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "category": category,
        "species": species,
        "matched_category": advice.guide.category,
        "matched_species": advice.guide.species,
        "confidence": advice.confidence,
    }
    with _LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")
