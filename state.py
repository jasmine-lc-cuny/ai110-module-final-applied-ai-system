"""Session state and persistence helpers for PawPal."""

import streamlit as st

from constants import CLINIC_DATA_PATH, DATA_PATH
from pawpal_system import Clinic, Owner, Scheduler, load_owners_from_json, save_owners_to_json


def _load_owners_from_disk() -> list[Owner]:
    if not DATA_PATH.exists():
        return []
    try:
        return load_owners_from_json(str(DATA_PATH))
    except Exception:
        return []


def _load_clinic_from_disk() -> Clinic | None:
    if not CLINIC_DATA_PATH.exists():
        return None
    try:
        return Clinic.load_from_json(str(CLINIC_DATA_PATH))
    except Exception:
        return None


def _owners_have_tasks(owners: list[Owner]) -> bool:
    return any(pet.tasks for owner in owners for pet in owner.pets)


def ensure_demo_data() -> None:
    """Seed demo data if the local files are missing or empty."""
    disk_owners = _load_owners_from_disk()
    disk_clinic = _load_clinic_from_disk()

    owners_missing_or_empty = not disk_owners
    tasks_missing = bool(disk_owners) and not _owners_have_tasks(disk_owners)
    clinic_missing = disk_clinic is None
    doctors_missing = clinic_missing or not disk_clinic.doctors
    staff_missing = clinic_missing or not disk_clinic.staff

    if (
        not owners_missing_or_empty
        and not tasks_missing
        and not clinic_missing
        and not doctors_missing
        and not staff_missing
    ):
        return

    if owners_missing_or_empty:
        from seed.seed_animals_distribution import seed_animals_list

        seed_animals_list()

    if staff_missing:
        from seed.seed_staff import seed_staff

        seed_staff()

    if doctors_missing:
        from seed.seed_doctors import seed_doctors

        seed_doctors()

    if owners_missing_or_empty or tasks_missing or clinic_missing:
        from seed.seed_random_appointments import seed_random_appointments

        seed_random_appointments()

    st.session_state.pop("owners", None)
    st.session_state.pop("clinic", None)


def get_owners() -> list[Owner]:
    ensure_demo_data()
    if "owners" not in st.session_state or not st.session_state.owners:
        disk_owners = _load_owners_from_disk()
        if disk_owners:
            st.session_state.owners = disk_owners
        elif "owners" not in st.session_state:
            st.session_state.owners = [Owner("Jordan")]
    return st.session_state.owners


def get_combined_owner() -> Owner:
    return Owner(
        "All Owners",
        pets=[pet for owner in get_owners() for pet in owner.pets],
    )


def get_scheduler() -> Scheduler:
    return Scheduler(get_combined_owner())


def save_owners(owners: list[Owner]) -> None:
    save_owners_to_json(owners, str(DATA_PATH))


def save_owner(owner: Owner) -> None:
    save_owners(get_owners())


def get_clinic() -> Clinic:
    ensure_demo_data()
    if "clinic" not in st.session_state or not st.session_state.clinic:
        disk_clinic = _load_clinic_from_disk()
        if disk_clinic is not None:
            st.session_state.clinic = disk_clinic
        elif "clinic" not in st.session_state:
            st.session_state.clinic = Clinic()
    return st.session_state.clinic


def save_clinic(clinic: Clinic) -> None:
    clinic.save_to_json(str(CLINIC_DATA_PATH))
