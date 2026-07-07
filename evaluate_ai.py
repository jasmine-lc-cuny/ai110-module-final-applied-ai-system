"""Simple reliability harness for the PawPal applied-AI layer."""

from __future__ import annotations

from pathlib import Path
import csv

from ai_system import advise_service
from ai_applied_prediagnostic import assess_symptoms
from ai_applied_medication_advisor import recommend_medication
from ai_applied_adoption_match import QuizAnswers, best_matches
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

    emergency_assessment = assess_symptoms("my dog had a seizure and collapsed")
    normal_assessment = assess_symptoms("itching and scratching a lot")
    if emergency_assessment.department == "Emergency" and normal_assessment.department == "Dermatology":
        print("PASS: Pre-diagnostic assessment matched Emergency guardrail and Dermatology retrieval correctly")
    else:
        print("FAIL: Pre-diagnostic assessment did not match expected departments")
        raise SystemExit(1)

    dog_oa_medication = recommend_medication("diagnosed with osteoarthritis, chronic joint pain", "dog")
    species_blocked_medication = recommend_medication("diagnosed with hyperthyroidism", "dog")
    if dog_oa_medication.medication == "Carprofen (Rimadyl)" and species_blocked_medication.medication is None:
        print("PASS: Medication advisor matched osteoarthritis retrieval and blocked a species-inappropriate suggestion")
    else:
        print("FAIL: Medication advisor did not behave as expected")
        raise SystemExit(1)

    quiz_answers = QuizAnswers(
        species_preference="dog", energy_level="low", grooming_tolerance="low",
        apartment=True, wants_kid_friendly=True,
    )
    top_matches = best_matches(quiz_answers, top_n=5)
    if len(top_matches) == 5 and top_matches[0].species == "dog" and top_matches[0].score >= top_matches[-1].score:
        print(f"PASS: Adoption match quiz ranked top breed '{top_matches[0].breed}' ({top_matches[0].label})")
    else:
        print("FAIL: Adoption match quiz did not return a valid ranked list")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
