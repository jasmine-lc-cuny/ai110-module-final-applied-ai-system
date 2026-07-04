"""Seed demo clients, tasks, calendar entries, and clinic appointments.

This script is meant to be run when you want the app to feel "alive" again
without manually clicking every form in Streamlit. It uses the current local
clock as its anchor, so the generated schedule lines up with today's date and
near-future appointment slots instead of stale fixed times.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

from pawpal_system import Appointment, Clinic, Doctor, Owner, Pet, Task, load_owners_from_json, save_owners_to_json

DATA_PATH = Path("data.json")
CLINIC_PATH = Path("clinic.json")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


@dataclass(frozen=True)
class ClientSeed:
    owner_name: str
    phone: str
    email: str
    pets: list[dict]


CLIENTS: list[ClientSeed] = [
    ClientSeed(
        owner_name="Ariana Stone",
        phone="(555) 410-2211",
        email="ariana.stone@example.com",
        pets=[
            {"name": "Maple", "species": "dog", "age": 4, "sex": "Female"},
            {"name": "Pico", "species": "cat", "age": 2, "sex": "Male"},
        ],
    ),
    ClientSeed(
        owner_name="Noah Bennett",
        phone="(555) 410-3344",
        email="noah.bennett@example.com",
        pets=[
            {"name": "Clover", "species": "rabbit", "age": 3, "sex": "Female"},
        ],
    ),
    ClientSeed(
        owner_name="Priya Kapoor",
        phone="(555) 410-7788",
        email="priya.kapoor@example.com",
        pets=[
            {"name": "Sunny", "species": "dog", "age": 6, "sex": "Male"},
            {"name": "Miso", "species": "cat", "age": 5, "sex": "Female"},
        ],
    ),
]


DOCTOR_MATCHES = {
    "dog": "general",
    "cat": "general",
    "rabbit": "internal",
}

FOLLOW_UP_TASKS = [
    ("Morning Walk", "walking", 30, "high", "daily"),
    ("Brush Coat", "grooming", 20, "medium", "once"),
    ("Breakfast", "special_services", 15, "medium", "daily"),
    ("Vet Appointment", "veterinary", 30, "high", "once"),
]


def _round_up_to_quarter(moment: datetime) -> datetime:
    """Return the next 15-minute slot at or after moment."""
    minutes = (moment.minute // 15 + 1) * 15
    if minutes == 60:
        return moment.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    return moment.replace(minute=minutes, second=0, microsecond=0)


def _time_after(moment: datetime, minutes: int) -> str:
    """Format a time string relative to the live clock."""
    future = moment + timedelta(minutes=minutes)
    return future.strftime("%H:%M")


def _ensure_clinic_defaults(clinic: Clinic) -> None:
    """Populate doctors if the clinic file is empty so appointments can be seeded."""
    if clinic.doctors:
        return

    clinic.doctors = [
        Doctor("Ava", "Patel", "general", department_name="General Practice", specialization="Primary Care", education="DVM", visit_fee=85.0),
        Doctor("Noah", "Kim", "surgery", department_name="Surgery", specialization="Soft Tissue Surgery", education="DVM, DACVS", visit_fee=145.0),
        Doctor("Nora", "Davis", "cardio", department_name="Cardiology", specialization="Cardiology", education="DVM, DACVIM", visit_fee=150.0),
    ]


def _doctor_for_species(clinic: Clinic, species: str) -> Doctor:
    """Pick a doctor that best fits the species, falling back to any active doctor."""
    desired = DOCTOR_MATCHES.get(species.lower())
    active_doctors = [doctor for doctor in clinic.doctors if doctor.active]

    if desired:
        for doctor in active_doctors:
            haystack = f"{doctor.department_name} {doctor.specialization} {doctor.username}".lower()
            if desired in haystack:
                return doctor

    return active_doctors[0] if active_doctors else clinic.doctors[0]


def _task_for_pet(index: int, base_clock: datetime, pet: Pet) -> Task:
    """Generate a task that sits close to the current clock for this pet."""
    title, category, duration, priority, frequency = FOLLOW_UP_TASKS[index % len(FOLLOW_UP_TASKS)]
    due_date = base_clock.date() if index < 3 else base_clock.date() + timedelta(days=index - 2)
    time_str = _time_after(base_clock, 15 + (index * 20))
    return Task(
        title=title,
        time=time_str,
        duration_minutes=duration,
        priority=priority,
        frequency=frequency,
        due_date=due_date,
        category=category,
        notes=f"Seeded from the live clock at {base_clock.strftime('%I:%M %p').lstrip('0')}",
        assignee=None,
    )


def seed_clients() -> None:
    """Seed demo clients into the app's data and clinic records."""
    now = datetime.now()
    clock_anchor = _round_up_to_quarter(now)

    if DATA_PATH.exists():
        owners = load_owners_from_json(str(DATA_PATH))
    else:
        owners = []

    if CLINIC_PATH.exists():
        clinic = Clinic.load_from_json(str(CLINIC_PATH))
    else:
        clinic = Clinic()

    _ensure_clinic_defaults(clinic)
    clinic.appointments = []

    owners_by_name = {owner.name.lower(): owner for owner in owners}

    for client in CLIENTS:
        owner = owners_by_name.get(client.owner_name.lower())
        if owner is None:
            owner = Owner(name=client.owner_name, phone=client.phone, email=client.email)
            owners.append(owner)
            owners_by_name[client.owner_name.lower()] = owner
        else:
            owner.phone = owner.phone or client.phone
            owner.email = owner.email or client.email

        for pet_index, pet_info in enumerate(client.pets):
            pet = owner.find_pet(pet_info["name"])
            if pet is None:
                pet = Pet(
                    name=pet_info["name"],
                    species=pet_info["species"],
                    age=pet_info.get("age"),
                    sex=pet_info.get("sex"),
                )
                owner.add_pet(pet)

            for task_offset in range(2):
                task = _task_for_pet(
                    pet_index * 2 + task_offset,
                    clock_anchor + timedelta(minutes=task_offset * 10),
                    pet,
                )
                pet.add_task(task)

            doctor = _doctor_for_species(clinic, pet.species)
            appointment_date = clock_anchor.date() + timedelta(days=min(pet_index, 1))
            appointment_time = _time_after(clock_anchor, 30 + pet_index * 25)
            clinic.appointments.append(
                Appointment(
                    owner_name=owner.name,
                    pet_name=pet.name,
                    doctor_username=doctor.username,
                    date=appointment_date,
                    time=appointment_time,
                    reason=f"New client intake for {pet.name}",
                    status="Pending",
                )
            )

    save_owners_to_json(owners, str(DATA_PATH))
    clinic.save_to_json(str(CLINIC_PATH))

    total_pets = sum(len(owner.pets) for owner in owners)
    total_tasks = sum(len(pet.tasks) for owner in owners for pet in owner.pets)
    print(f"🕒 Seeded {len(CLIENTS)} clients, {total_pets} pets, {total_tasks} tasks, and {len(clinic.appointments)} appointments.")
    print(f"   Clock anchor: {clock_anchor.strftime('%A, %B %d, %Y at %I:%M %p').lstrip('0')}")


if __name__ == "__main__":
    seed_clients()
