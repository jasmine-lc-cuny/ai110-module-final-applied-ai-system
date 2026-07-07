"""AI pre-diagnostic vet assessment.

A second, distinct applied-AI use case from ai_system.py's service-task advice
and ai_applied_agentic_loop.py's staff/slot planner: this module turns a
free-text symptom description into (1) a retrieval-backed specialty match
(RAG, same keyword-scoring style as ai_system.py) and (2) a doctor
recommendation that checks the matched specialist's actual availability
today, escalating to the next best candidate if they're fully booked.

Unlike the descriptive-only "guardrail" text in ai_guides.csv, this module
also enforces one guardrail in real code: any emergency keyword in the
symptom text short-circuits the match to Emergency/urgent care, regardless
of what else was typed. This is never a diagnosis — it only routes the
owner toward the right specialist and appointment slot.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
import csv
import json

from availability import find_available_slots

MAX_DOCTOR_ATTEMPTS = 3
FALLBACK_DEPARTMENT = "General Practice"

EMERGENCY_KEYWORDS = (
    "seizure",
    "seizures",
    "collapse",
    "collapsed",
    "unconscious",
    "unresponsive",
    "difficulty breathing",
    "cant breathe",
    "can't breathe",
    "cannot breathe",
    "choking",
    "heavy bleeding",
    "uncontrolled bleeding",
    "hit by car",
    "poison",
    "poisoned",
    "toxic ingestion",
    "straining to urinate",
)


@dataclass(frozen=True)
class SymptomGuide:
    department: str
    urgency: str
    keywords: tuple[str, ...]
    explanation: str
    guardrail: str


@dataclass(frozen=True)
class SymptomAssessment:
    department: str
    urgency: str
    confidence: float
    explanation: str
    guardrail: str


@dataclass(frozen=True)
class PlanStep:
    action: str
    detail: str


@dataclass
class DoctorRecommendation:
    assessment: SymptomAssessment
    doctor: object | None
    slot_start: str | None
    slot_end: str | None
    trace: list[PlanStep] = field(default_factory=list)
    success: bool = False


def _load_guides(path: str | Path) -> list[SymptomGuide]:
    guides: list[SymptomGuide] = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            guides.append(
                SymptomGuide(
                    department=row["department"],
                    urgency=row["urgency"],
                    keywords=tuple(part.strip().lower() for part in row["keywords"].split(";") if part.strip()),
                    explanation=row["explanation"],
                    guardrail=row["guardrail"],
                )
            )
    return guides


_GUIDES_PATH = Path(__file__).resolve().parent / "data" / "symptom_guides.csv"
_GUIDES = _load_guides(_GUIDES_PATH) if _GUIDES_PATH.exists() else []
_LOG_PATH = Path(__file__).resolve().parent / "logs" / "prediagnostic_traces.jsonl"


def assess_symptoms(symptom_text: str) -> SymptomAssessment:
    """Retrieve a specialty match for a free-text symptom description.

    Checks the hardcoded EMERGENCY_KEYWORDS guardrail first, which
    overrides any keyword-score match. Falls back to General Practice with
    low confidence if nothing in the corpus matches at all."""
    text_key = symptom_text.lower()

    for keyword in EMERGENCY_KEYWORDS:
        if keyword in text_key:
            assessment = SymptomAssessment(
                department="Emergency",
                urgency="emergency",
                confidence=0.95,
                explanation=f"'{keyword}' indicates a potential emergency.",
                guardrail="Do not wait for a scheduled appointment; contact an emergency vet immediately.",
            )
            _log_assessment(symptom_text, assessment)
            return assessment

    best = None
    best_score = 0.0
    for guide in _GUIDES:
        score = sum(1.0 for keyword in guide.keywords if keyword in text_key)
        if score > best_score:
            best = guide
            best_score = score

    if best is None:
        assessment = SymptomAssessment(
            department=FALLBACK_DEPARTMENT,
            urgency="routine",
            confidence=0.3,
            explanation="No specific symptoms were recognized, so General Practice is a safe starting point.",
            guardrail="This is a broad starting point; describe symptoms in more detail for a better match.",
        )
    else:
        confidence = min(0.95, 0.5 + best_score * 0.15)
        assessment = SymptomAssessment(
            department=best.department,
            urgency=best.urgency,
            confidence=round(confidence, 2),
            explanation=best.explanation,
            guardrail=best.guardrail,
        )

    _log_assessment(symptom_text, assessment)
    return assessment


def recommend_doctor(assessment: SymptomAssessment, clinic, target_date: date | None = None) -> DoctorRecommendation:
    """Pick the best available active doctor for `assessment.department`,
    checking today's appointments for openings and escalating to the next
    matching candidate (up to MAX_DOCTOR_ATTEMPTS) if the first is fully
    booked. Falls back to General Practice, then to any active doctor, if
    no doctor in the matched department exists."""
    target_date = target_date or date.today()
    trace: list[PlanStep] = []

    active_doctors = [doctor for doctor in clinic.doctors if doctor.active]
    candidates = [doctor for doctor in active_doctors if doctor.department_name == assessment.department]
    if candidates:
        trace.append(PlanStep("plan", f"Matched department '{assessment.department}': {len(candidates)} active doctor(s) available."))
    else:
        candidates = [doctor for doctor in active_doctors if doctor.department_name == FALLBACK_DEPARTMENT]
        if candidates:
            trace.append(PlanStep("plan", f"No active doctor in '{assessment.department}'; falling back to {FALLBACK_DEPARTMENT}."))
        else:
            candidates = active_doctors
            trace.append(PlanStep("plan", f"No active doctor in '{assessment.department}' or {FALLBACK_DEPARTMENT}; trying any active doctor."))

    if not candidates:
        trace.append(PlanStep("fail", "No active doctors at all — cannot recommend anyone."))
        recommendation = DoctorRecommendation(assessment, None, None, None, trace, False)
        _log_recommendation(recommendation)
        return recommendation

    for attempt, doctor in enumerate(candidates[:MAX_DOCTOR_ATTEMPTS], start=1):
        busy = [
            (appt.time, 30)
            for appt in clinic.appointments
            if appt.doctor_username == doctor.username
            and appt.date == target_date
            and appt.status != "Cancelled"
        ]
        slots = find_available_slots(busy)
        if not slots:
            trace.append(PlanStep("check", f"Attempt {attempt}: {doctor.full_name} has no open slots today. Trying next candidate."))
            continue

        slot_start, slot_end = slots[0]
        trace.append(PlanStep("act", f"Attempt {attempt}: {doctor.full_name} has an opening at {slot_start}-{slot_end}."))
        recommendation = DoctorRecommendation(assessment, doctor, slot_start, slot_end, trace, True)
        _log_recommendation(recommendation)
        return recommendation

    trace.append(PlanStep("fail", f"Exhausted {min(len(candidates), MAX_DOCTOR_ATTEMPTS)} candidate(s) with no open slot today."))
    recommendation = DoctorRecommendation(assessment, None, None, None, trace, False)
    _log_recommendation(recommendation)
    return recommendation


def _log_assessment(symptom_text: str, assessment: SymptomAssessment) -> None:
    _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "kind": "assessment",
        "symptom_text": symptom_text,
        "department": assessment.department,
        "urgency": assessment.urgency,
        "confidence": assessment.confidence,
    }
    with _LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def _log_recommendation(recommendation: DoctorRecommendation) -> None:
    _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "kind": "recommendation",
        "department": recommendation.assessment.department,
        "success": recommendation.success,
        "doctor": recommendation.doctor.full_name if recommendation.doctor else None,
        "slot_start": recommendation.slot_start,
        "slot_end": recommendation.slot_end,
        "trace": [{"action": step.action, "detail": step.detail} for step in recommendation.trace],
    }
    with _LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")
