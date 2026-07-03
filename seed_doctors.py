"""Seed a roster of clinic doctors into clinic.json.

This preserves any existing services, appointments, and staff while restoring
the random doctor roster used by the appointments and clinic pages.
"""

import random
import sys
from pathlib import Path

from pawpal_system import Clinic, Doctor

CLINIC_PATH = "clinic.json"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DOCTOR_PROFILES = [
    ("Ava", "Patel", "general", "Small Animal Medicine", "DVM", 85.0),
    ("Noah", "Kim", "surgery", "Surgery", "DVM, DACVS", 145.0),
    ("Mia", "Johnson", "dent", "Dentistry", "DVM", 110.0),
    ("Lucas", "Garcia", "derm", "Dermatology", "DVM", 100.0),
    ("Zoe", "Martinez", "exotics", "Exotics", "DVM", 120.0),
    ("Ethan", "Brown", "urgent", "Emergency", "DVM", 130.0),
    ("Nora", "Davis", "cardio", "Cardiology", "DVM, DACVIM", 150.0),
    ("Levi", "Wilson", "ortho", "Orthopedics", "DVM", 135.0),
]


def seed_doctors():
    """Replace the clinic's doctor roster, preserving all other clinic records."""
    if Path(CLINIC_PATH).exists():
        clinic = Clinic.load_from_json(CLINIC_PATH)
    else:
        clinic = Clinic()

    clinic.doctors = []
    for first_name, last_name, username, department, specialization, fee in DOCTOR_PROFILES:
        clinic.doctors.append(
            Doctor(
                first_name=first_name,
                last_name=last_name,
                username=username,
                department_name=department,
                specialization=specialization,
                education="Veterinary School",
                visit_fee=fee,
                active=random.random() < 0.95,
            )
        )

    clinic.save_to_json(CLINIC_PATH)
    print(f"Doctors seeded: {len(clinic.doctors)} records restored.")


if __name__ == "__main__":
    seed_doctors()
