"""AI medication advisor: recommend a medication for a diagnosed condition,
strictly from each medication's real labeled (or, where noted, extra-label)
indication - never a dose, and never a species this corpus doesn't cover.

A third distinct applied-AI use case, alongside ai_system.py's service-task
advice and ai_applied_prediagnostic.py's symptom-to-specialty triage: this
one takes a firm diagnosis/condition (not raw symptoms) and looks up which
curated medication's real-world label indication matches it.

The one guardrail enforced in actual code (not just descriptive text) here
is species safety: a medication is never suggested for a species its entry
doesn't list, even if its keywords otherwise score highest - a hard filter,
not just a caution appended to the message.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import csv
import json


@dataclass(frozen=True)
class MedicationGuide:
    medication: str
    species: tuple[str, ...]
    label_status: str
    condition_keywords: tuple[str, ...]
    indication: str
    guardrail: str


@dataclass(frozen=True)
class MedicationRecommendation:
    medication: str | None
    label_status: str | None
    indication: str | None
    guardrail: str | None
    confidence: float
    explanation: str


def _load_guides(path: str | Path) -> list[MedicationGuide]:
    guides: list[MedicationGuide] = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            guides.append(
                MedicationGuide(
                    medication=row["medication"],
                    species=tuple(part.strip().lower() for part in row["species"].split(";") if part.strip()),
                    label_status=row["label_status"],
                    condition_keywords=tuple(
                        part.strip().lower() for part in row["condition_keywords"].split(";") if part.strip()
                    ),
                    indication=row["indication"],
                    guardrail=row["guardrail"],
                )
            )
    return guides


_GUIDES_PATH = Path(__file__).resolve().parent / "data" / "medication_guides.csv"
_GUIDES = _load_guides(_GUIDES_PATH) if _GUIDES_PATH.exists() else []
_LOG_PATH = Path(__file__).resolve().parent / "logs" / "medication_advice.jsonl"


def recommend_medication(condition_text: str, species: str) -> MedicationRecommendation:
    """Recommend a medication for a diagnosed `condition_text`, restricted to
    entries labeled for `species` - a hard filter, not just a scoring bonus,
    so a species-inappropriate medication is never suggested."""
    species_key = species.lower()
    condition_key = condition_text.lower()

    species_candidates = [guide for guide in _GUIDES if species_key in guide.species]
    if not species_candidates:
        recommendation = MedicationRecommendation(
            medication=None,
            label_status=None,
            indication=None,
            guardrail=None,
            confidence=0.0,
            explanation=f"No medication in this curated corpus is labeled for '{species}'. Consult your veterinarian.",
        )
        _log_recommendation(condition_text, species, recommendation)
        return recommendation

    best = None
    best_score = 0.0
    for guide in species_candidates:
        score = sum(1.0 for keyword in guide.condition_keywords if keyword in condition_key)
        if score > best_score:
            best = guide
            best_score = score

    if best is None:
        recommendation = MedicationRecommendation(
            medication=None,
            label_status=None,
            indication=None,
            guardrail=None,
            confidence=0.0,
            explanation=(
                "No medication in this curated corpus matches that condition. "
                "This is a small, curated reference, not a full formulary — consult your veterinarian."
            ),
        )
    else:
        confidence = min(0.95, 0.5 + best_score * 0.15)
        recommendation = MedicationRecommendation(
            medication=best.medication,
            label_status=best.label_status,
            indication=best.indication,
            guardrail=best.guardrail,
            confidence=round(confidence, 2),
            explanation=best.indication,
        )

    _log_recommendation(condition_text, species, recommendation)
    return recommendation


def _log_recommendation(condition_text: str, species: str, recommendation: MedicationRecommendation) -> None:
    _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "condition_text": condition_text,
        "species": species,
        "medication": recommendation.medication,
        "label_status": recommendation.label_status,
        "confidence": recommendation.confidence,
    }
    with _LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")
