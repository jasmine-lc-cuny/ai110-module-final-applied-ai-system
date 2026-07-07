"""Agentic booking planner.

Unlike ai_system.py's advise_service() (a single retrieve-then-respond RAG
call), this is a multi-step plan -> act -> check -> revise loop: it retrieves
care guidance, proposes a staff member and time slot, checks its own proposal
against the pet's existing schedule for a conflict, and — if one is found —
revises by trying the next staff member, up to MAX_ATTEMPTS times, before
giving up. Every step of that reasoning is recorded on the returned plan and
appended to logs/agent_traces.jsonl.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
import json

from ai_system import advise_service
from availability import find_available_slots

MAX_ATTEMPTS = 3
_TRACE_LOG_PATH = Path(__file__).resolve().parent / "logs" / "agent_traces.jsonl"


@dataclass(frozen=True)
class PlanStep:
    action: str
    detail: str


@dataclass
class BookingPlan:
    task_title: str | None
    staff_name: str | None
    slot_start: str | None
    slot_end: str | None
    confidence: float | None
    trace: list[PlanStep] = field(default_factory=list)
    success: bool = False


def plan_booking(
    *,
    category: str,
    pet,
    title_options: list[str],
    active_staff: list,
    combined_owner,
    target_date: date | None = None,
) -> BookingPlan:
    """Plan a booking for `pet` in `category`: retrieve guidance (RAG), then
    try each active staff member's earliest open slot, checking it against
    the pet's own schedule and revising (trying the next staff member) if
    there's a conflict. Returns a BookingPlan with a full reasoning trace."""
    target_date = target_date or date.today()
    trace: list[PlanStep] = []

    # Step 1 — Plan: retrieve care guidance via the existing RAG layer.
    # advice.guide.recommended_titles isn't pre-filtered against this
    # category's actual title_options (bookings.py's own UI does that
    # filtering itself), so repeat the same defensive filter here.
    advice = advise_service(category, pet.species, title_options)
    if advice is not None:
        valid_recommended = [title for title in advice.guide.recommended_titles if title in title_options]
        task_title = valid_recommended[0] if valid_recommended else (title_options[0] if title_options else None)
        confidence = advice.confidence
        trace.append(
            PlanStep(
                "plan",
                f"Retrieved guidance for {pet.species} {category}: {advice.explanation} "
                f"(confidence {confidence:.2f}). Recommended task: {task_title}.",
            )
        )
    else:
        task_title = title_options[0] if title_options else None
        confidence = None
        trace.append(PlanStep("plan", "No retrieval guidance matched; defaulting to the first listed task."))

    if task_title is None:
        trace.append(PlanStep("fail", "No task options exist for this category — nothing to plan."))
        return _finish(category, pet.name, BookingPlan(None, None, None, None, confidence, trace, False))

    if not active_staff:
        trace.append(PlanStep("fail", "No active staff in this section to assign — cannot propose a slot."))
        return _finish(category, pet.name, BookingPlan(task_title, None, None, None, confidence, trace, False))

    # Search on 15-minute boundaries — matching the booking form's Hour/
    # Minute dropdowns (00/15/30/45) — rather than the task's own duration,
    # so a proposed slot is always one the form can directly preselect.
    slot_minutes = 15
    pet_busy_times = {task.time for task in pet.tasks if task.due_date == target_date}

    # Step 2/3/4 — Act, check, revise: try each staff member's earliest slot
    # in turn, rejecting one that collides with a task the pet already has.
    for attempt, staff in enumerate(active_staff[:MAX_ATTEMPTS], start=1):
        staff_busy = [
            (task.time, task.duration_minutes)
            for owner_pet in combined_owner.pets
            for task in owner_pet.tasks
            if task.assignee == staff.full_name and task.due_date == target_date
        ]
        slots = find_available_slots(staff_busy, slot_minutes=slot_minutes)
        if not slots:
            trace.append(PlanStep("check", f"Attempt {attempt}: {staff.full_name} has no open slots today. Trying next staff member."))
            continue

        # Search every slot this staff member has free — not just the
        # earliest — before giving up on them. Two staff with no prior
        # bookings both offer 07:00 first; escalating to "the next staff"
        # on a single rejected slot would just hit the same conflict again.
        conflict_free = next((slot for slot in slots if slot[0] not in pet_busy_times), None)
        if conflict_free is None:
            trace.append(
                PlanStep(
                    "check",
                    f"Attempt {attempt}: checked all {len(slots)} open slots for {staff.full_name}; every one "
                    f"conflicts with {pet.name}'s existing schedule. Revising: trying the next staff member.",
                )
            )
            continue

        slot_start, slot_end = conflict_free
        trace.append(
            PlanStep(
                "act",
                f"Attempt {attempt}: proposed {staff.full_name} at {slot_start}-{slot_end} — checked against "
                f"{pet.name}'s existing schedule, no conflict found.",
            )
        )
        plan = BookingPlan(task_title, staff.full_name, slot_start, slot_end, confidence, trace, True)
        return _finish(category, pet.name, plan)

    trace.append(PlanStep("fail", f"Exhausted {min(len(active_staff), MAX_ATTEMPTS)} staff members with no conflict-free slot."))
    return _finish(category, pet.name, BookingPlan(task_title, None, None, None, confidence, trace, False))


def _finish(category: str, pet_name: str, plan: BookingPlan) -> BookingPlan:
    _log_trace(category, pet_name, plan)
    return plan


def _log_trace(category: str, pet_name: str, plan: BookingPlan) -> None:
    _TRACE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "category": category,
        "pet": pet_name,
        "success": plan.success,
        "task_title": plan.task_title,
        "staff_name": plan.staff_name,
        "slot_start": plan.slot_start,
        "slot_end": plan.slot_end,
        "confidence": plan.confidence,
        "trace": [{"action": step.action, "detail": step.detail} for step in plan.trace],
    }
    with _TRACE_LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")
