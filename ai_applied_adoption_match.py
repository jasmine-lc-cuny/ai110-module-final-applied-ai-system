"""Adoption match quiz scoring: takes a short set of lifestyle answers and
scores every seeded breed against them, RAG-style (same retrieval/scoring
shape as ai_system.py and ai_applied_prediagnostic.py — score each
candidate against the query, rank, return the best).

Scoring is deliberately axis-based rather than free-text keyword matching,
since the quiz answers are already structured (radio/checkbox choices),
not prose — each of the four axes maps directly onto a BreedTraits field.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json

from breed_personality import breed_personality
from breed_traits import CAT_BREED_TRAITS, DOG_BREED_TRAITS, breed_traits

_GROOMING_RANK = {"low": 0, "medium": 1, "high": 2}

_LOG_PATH = Path(__file__).resolve().parent / "logs" / "adoption_match_traces.jsonl"


@dataclass(frozen=True)
class QuizAnswers:
    species_preference: str   # "dog" | "cat" | "either"
    energy_level: str         # "low" | "medium" | "high" — desired
    grooming_tolerance: str   # "low" | "medium" | "high" — max upkeep willing to do
    apartment: bool           # True = lives in an apartment/small space
    wants_kid_friendly: bool  # True = must be good with kids


@dataclass(frozen=True)
class BreedMatch:
    species: str
    breed: str
    score: int
    max_score: int
    label: str
    personality: str
    trace: tuple[str, ...]


def score_breed(answers: QuizAnswers, species: str, breed: str) -> BreedMatch:
    """Score a single breed against the quiz answers on 4 equally-weighted
    axes (energy, grooming, apartment fit, kid-friendliness)."""
    traits = breed_traits(species, breed)
    trace: list[str] = []
    score = 0

    if traits.energy_level == answers.energy_level:
        score += 1
        trace.append(f"✓ Energy level matches ({traits.energy_level}).")
    else:
        trace.append(f"✗ Energy level is {traits.energy_level}, you wanted {answers.energy_level}.")

    if _GROOMING_RANK[answers.grooming_tolerance] >= _GROOMING_RANK[traits.grooming_needs]:
        score += 1
        trace.append(f"✓ Grooming needs ({traits.grooming_needs}) fit your tolerance.")
    else:
        trace.append(f"✗ Needs more grooming ({traits.grooming_needs}) than you're up for.")

    if not answers.apartment or traits.apartment_friendly:
        score += 1
        trace.append("✓ Fits an apartment/small space." if answers.apartment else "✓ You have room to spare, so space isn't a constraint.")
    else:
        trace.append("✗ Not well suited to apartment living.")

    if not answers.wants_kid_friendly or traits.kid_friendly:
        score += 1
        trace.append("✓ Good with kids." if answers.wants_kid_friendly else "✓ Kid-friendliness wasn't required.")
    else:
        trace.append("✗ Not typically recommended around young kids.")

    max_score = 4
    if score >= 3:
        label = "✅ Good match"
    elif score == 2:
        label = "⚠️ Caution"
    else:
        label = "❌ Not ideal"

    return BreedMatch(
        species=species,
        breed=breed,
        score=score,
        max_score=max_score,
        label=label,
        personality=breed_personality(species, breed) or "",
        trace=tuple(trace),
    )


def best_matches(answers: QuizAnswers, top_n: int = 5) -> list[BreedMatch]:
    """Score every breed matching the species preference and return the
    top_n highest-scoring, ties broken alphabetically by breed name."""
    candidates: list[tuple[str, str]] = []
    if answers.species_preference in ("dog", "either"):
        candidates += [("dog", breed) for breed in DOG_BREED_TRAITS]
    if answers.species_preference in ("cat", "either"):
        candidates += [("cat", breed) for breed in CAT_BREED_TRAITS]

    matches = [score_breed(answers, species, breed) for species, breed in candidates]
    matches.sort(key=lambda match: (-match.score, match.breed))
    top = matches[:top_n]
    _log_matches(answers, top)
    return top


def _log_matches(answers: QuizAnswers, top: list[BreedMatch]) -> None:
    _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "answers": {
            "species_preference": answers.species_preference,
            "energy_level": answers.energy_level,
            "grooming_tolerance": answers.grooming_tolerance,
            "apartment": answers.apartment,
            "wants_kid_friendly": answers.wants_kid_friendly,
        },
        "top_matches": [
            {"species": match.species, "breed": match.breed, "score": match.score, "label": match.label}
            for match in top
        ],
    }
    with _LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")
