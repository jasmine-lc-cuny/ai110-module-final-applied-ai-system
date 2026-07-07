"""Seed random appointments into the current PawPal pets and clinic."""

from __future__ import annotations

import random
import sys
import argparse
from calendar import monthrange
from datetime import date, datetime, timedelta, time
from pathlib import Path

from constants import CATEGORY_TASK_TITLES, CATEGORY_TO_SECTION
from pawpal_system import Appointment, Clinic, Doctor, Task, load_owners_from_json, save_owners_to_json

DATA_PATH = Path("data.json")
CLINIC_PATH = Path("clinic.json")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


DOCTOR_FALLBACKS = [
    Doctor("Ava", "Patel", "general", department_name="General Practice", specialization="Primary Care", education="DVM", visit_fee=85.0),
    Doctor("Noah", "Kim", "surgery", department_name="Surgery", specialization="Soft Tissue Surgery", education="DVM, DACVS", visit_fee=145.0),
    Doctor("Nora", "Davis", "cardio", department_name="Cardiology", specialization="Cardiology", education="DVM, DACVIM", visit_fee=150.0),
]

REASONS_BY_SPECIES = {
    "dog": ["Annual exam", "Vaccination follow-up", "Ear infection check", "Dental cleaning consult"],
    "cat": ["Annual exam", "Vaccination follow-up", "Weight check", "Dental consult"],
    "rabbit": ["Nail trim consult", "Digestive health check", "New patient exam"],
}

STATUS_OPTIONS = ["Pending", "Confirmed", "Completed"]

# One task per pet per eligible category per day, using the same full task
# lists the live booking form offers (constants.CATEGORY_TASK_TITLES) instead
# of a narrow hand-picked subset — otherwise the seeded demo only ever shows
# 1-2 of each category's real task variety.
CATEGORY_TASK_DEFAULTS = {
    "walking": (30, "medium", "daily"),
    "grooming": (25, "medium", "once"),
    "training": (45, "high", "once"),
    "special_services": (15, "medium", "daily"),
    "sitting": (60, "medium", "once"),
}

DOG_SERVICE_CATEGORIES = ["walking", "grooming", "training", "special_services"]
CAT_SERVICE_CATEGORIES = ["grooming", "sitting"]
DAY_START_MINUTES = 7 * 60
DAY_END_MINUTES = 20 * 60


def _round_up_to_quarter(moment: datetime) -> datetime:
    minutes = (moment.minute // 15 + 1) * 15
    if minutes == 60:
        return moment.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    return moment.replace(minute=minutes, second=0, microsecond=0)


def _time_within_window(day: datetime, offset_minutes: int, duration_minutes: int = 0) -> str:
    """Return an HH:MM time within the 7 AM to 8 PM seeding window."""
    latest_start = DAY_END_MINUTES - max(duration_minutes, 1)
    window_size = max(latest_start - DAY_START_MINUTES + 1, 1)
    minute_of_day = DAY_START_MINUTES + (offset_minutes % window_size)
    seeded = datetime.combine(day.date(), time(hour=0, minute=0)) + timedelta(minutes=minute_of_day)
    return seeded.strftime("%H:%M")


def _ensure_doctors(clinic: Clinic) -> None:
    if clinic.doctors:
        return
    clinic.doctors = DOCTOR_FALLBACKS[:]


def _doctor_for_species(clinic: Clinic, species: str) -> Doctor:
    active_doctors = [doctor for doctor in clinic.doctors if doctor.active] or clinic.doctors
    if not active_doctors:
        return DOCTOR_FALLBACKS[0]

    species_key = species.lower()
    preferred = {
        "dog": ("general", "primary"),
        "cat": ("general", "primary"),
        "rabbit": ("internal", "exotic"),
    }.get(species_key)

    if preferred:
        for doctor in active_doctors:
            haystack = f"{doctor.department_name} {doctor.specialization} {doctor.username}".lower()
            if any(token in haystack for token in preferred):
                return doctor

    return random.choice(active_doctors)


def _staff_for_category(clinic: Clinic, category: str):
    """Return an active staff member for the matching service section, if any."""
    section = CATEGORY_TO_SECTION.get(category)
    if not section:
        return None
    active_staff = [member for member in clinic.staff_in_section(section) if member.active]
    if not active_staff:
        active_staff = clinic.staff_in_section(section)
    return random.choice(active_staff) if active_staff else None


def _month_dates(anchor: datetime) -> list[date]:
    """Every calendar date in anchor's month (the whole month, not just today
    forward), so the monthly calendar and day-by-day category pages both have
    real data to show instead of a single populated day."""
    days_in_month = monthrange(anchor.year, anchor.month)[1]
    return [date(anchor.year, anchor.month, day) for day in range(1, days_in_month + 1)]


def _seed_service_tasks(owners, clinic: Clinic, anchor: datetime, *, species: str, categories: list[str]) -> int:
    """Give every matching pet one task in each eligible category, on every
    day of the month, so every service section has coverage all month long
    instead of just today."""
    seeded = 0
    month_dates = _month_dates(anchor)
    for owner_index, owner in enumerate(owners):
        for pet_index, pet in enumerate(owner.pets):
            if pet.species.lower() != species:
                continue

            pet.tasks = []
            for day_offset, due_date in enumerate(month_dates):
                for task_offset, category in enumerate(categories):
                    titles = CATEGORY_TASK_TITLES.get(category, [])
                    if not titles:
                        continue
                    title = titles[(owner_index + pet_index + task_offset + day_offset) % len(titles)]
                    duration, priority, frequency = CATEGORY_TASK_DEFAULTS.get(category, (30, "medium", "once"))
                    assigned_staff = _staff_for_category(clinic, category)
                    time_str = _time_within_window(
                        anchor,
                        offset_minutes=10 + owner_index * 6 + pet_index * 9 + task_offset * 37 + day_offset * 19,
                        duration_minutes=duration,
                    )
                    task = Task(
                        title=title,
                        time=time_str,
                        duration_minutes=duration,
                        priority=priority,
                        frequency=frequency,
                        due_date=due_date,
                        category=category,
                        notes=f"Seeded task for {due_date.strftime('%B %d, %Y')}",
                        assignee=assigned_staff.full_name if assigned_staff else None,
                    )
                    if due_date < date.today():
                        task.completed = True
                    pet.add_task(task)
                    seeded += 1
    return seeded


APPOINTMENTS_PER_DAY = 10


def _status_for_date(appt_date: date) -> str:
    """Past visits read as resolved, today's mix like a real day in progress,
    future ones are still just scheduled — not just a flat random status."""
    today = date.today()
    if appt_date < today:
        return random.choice(["Completed", "Cancelled"])
    if appt_date == today:
        return random.choice(STATUS_OPTIONS)
    return random.choice(["Pending", "Confirmed"])


def _seed_vet_appointments(owners, clinic: Clinic, anchor: datetime) -> list[tuple[str, str, str, date, str, str, str]]:
    """Spread appointments across every day of the month instead of a single
    18-pet sample crammed into 3 days, so the clinic calendar has real
    month-long coverage."""
    clinic.appointments = []
    all_pets = [pet for owner in owners for pet in owner.pets]
    if not all_pets:
        return []

    rows = []
    appts_per_day = min(APPOINTMENTS_PER_DAY, len(all_pets))
    for appt_date in _month_dates(anchor):
        for slot_index, pet in enumerate(random.sample(all_pets, appts_per_day)):
            owner = next(owner for owner in owners if pet in owner.pets)
            doctor = _doctor_for_species(clinic, pet.species)
            time_str = _time_within_window(anchor, offset_minutes=20 + slot_index * 17, duration_minutes=30)
            reason = random.choice(REASONS_BY_SPECIES.get(pet.species.lower(), ["General wellness check", "Follow-up visit"]))
            status = _status_for_date(appt_date)

            clinic.appointments.append(
                Appointment(
                    owner_name=owner.name,
                    pet_name=pet.name,
                    doctor_username=doctor.username,
                    date=appt_date,
                    time=time_str,
                    reason=reason,
                    status=status,
                )
            )
            # Mirror as a Task, same as the live Book Appointment dialog does —
            # otherwise the "veterinary" category has appointments but no
            # Tasks, so Clinic Today's/Monthly Schedule would stay empty.
            # Cancelled appointments have no linked task, matching how
            # cancelling one live removes its mirrored task.
            if status != "Cancelled":
                pet.add_task(
                    Task(
                        title="Vet Appointment",
                        time=time_str,
                        duration_minutes=30,
                        priority="high",
                        frequency="once",
                        notes=reason,
                        due_date=appt_date,
                        category="veterinary",
                        assignee=doctor.full_name,
                        completed=status == "Completed",
                    )
                )
            rows.append((owner.name, pet.name, doctor.full_name, appt_date, time_str, status, reason))
    return rows


def _clear_schedule_layer(owners, clinic: Clinic) -> None:
    """Remove existing tasks and appointments so each seed mode starts clean."""
    for owner in owners:
        for pet in owner.pets:
            pet.tasks = []
    clinic.appointments = []


def seed_random_appointments(mode: str = "services") -> None:
    """Seed dog/cat services, vet appointments, or both."""
    now = datetime.now()
    anchor = _round_up_to_quarter(now)

    owners = load_owners_from_json(str(DATA_PATH)) if DATA_PATH.exists() else []
    clinic = Clinic.load_from_json(str(CLINIC_PATH)) if CLINIC_PATH.exists() else Clinic()

    _ensure_doctors(clinic)

    if not owners:
        print("No owners found in data.json. Run the animal/client seed first.")
        return

    random.seed(anchor.toordinal())
    _clear_schedule_layer(owners, clinic)

    appointment_rows = []
    service_task_count = 0

    if mode in {"services", "all", "dogs"}:
        service_task_count += _seed_service_tasks(owners, clinic, anchor, species="dog", categories=DOG_SERVICE_CATEGORIES)
    if mode in {"services", "all", "cats"}:
        service_task_count += _seed_service_tasks(owners, clinic, anchor, species="cat", categories=CAT_SERVICE_CATEGORIES)

    if mode in {"all", "vet"}:
        appointment_rows = _seed_vet_appointments(owners, clinic, anchor)

    save_owners_to_json(owners, str(DATA_PATH))
    clinic.save_to_json(str(CLINIC_PATH))

    if service_task_count:
        print(f"🐾 Seeded {service_task_count} service tasks for mode '{mode}'.")
    if appointment_rows:
        print(f"📅 Seeded {len(appointment_rows)} random appointments into clinic.json")
        for owner_name, pet_name, doctor_name, due_date, time_str, status, reason in appointment_rows[:10]:
            print(f"   {due_date.isoformat()} {time_str} - {owner_name} / {pet_name} with {doctor_name} [{status}] ({reason})")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed PawPal demo services and appointments.")
    parser.add_argument(
        "mode",
        nargs="?",
        default="services",
        choices=["services", "all", "dogs", "cats", "vet"],
        help="What to seed: services (dogs + cats), dog services, cat services, vet appointments, or all.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    seed_random_appointments(args.mode)
