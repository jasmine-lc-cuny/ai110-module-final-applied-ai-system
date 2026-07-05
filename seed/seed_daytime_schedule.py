"""Rebuild PawPal's demo schedule inside the daytime window.

This is a thin wrapper around the existing seeders so the saved files stay
clean, the generated schedule lands between 7 AM and 8 PM, and each service
task gets a matching staff assignee when the clinic has staff loaded.
"""

from __future__ import annotations

from seed.seed_doctors import seed_doctors
from seed.seed_random_appointments import seed_random_appointments
from seed.seed_staff import seed_staff


def seed_daytime_schedule() -> None:
    """Refresh staff, doctors, service tasks, and appointments in one pass."""
    seed_staff()
    seed_doctors()
    seed_random_appointments("all")


if __name__ == "__main__":
    seed_daytime_schedule()
