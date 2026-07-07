"""Custom sub-menu pickers for booking-form task details (veterinary reasons, dog cafe menu)."""

import streamlit as st

from constants import (
    A_LA_BARK_MENU,
    INJECTION_MEDICATION_CATEGORIES,
    INJECTION_MEDICATION_OPTIONS,
    INJECTION_MEDICATION_PAIN_OPTIONS_BY_SPECIES,
    VETERINARY_TASK_REASONS,
    VETERINARY_TASK_REASONS_BY_SPECIES,
)


def render_veterinary_reason_picker(title: str, species: str, key_prefix: str = "vet") -> str | None:
    species_key = species.lower()

    if title == "Injection Medication":
        category = st.selectbox("Medication Category", INJECTION_MEDICATION_CATEGORIES, key=f"{key_prefix}_med_category")
        if category == "Pain & Arthritis Management":
            medication_options = INJECTION_MEDICATION_PAIN_OPTIONS_BY_SPECIES.get(species_key, INJECTION_MEDICATION_PAIN_OPTIONS_BY_SPECIES["dog"])
        else:
            medication_options = INJECTION_MEDICATION_OPTIONS[category]
        return st.selectbox("Medication", medication_options, key=f"{key_prefix}_med_select_{category}")

    if title in VETERINARY_TASK_REASONS_BY_SPECIES:
        species_options = VETERINARY_TASK_REASONS_BY_SPECIES[title].get(species_key, VETERINARY_TASK_REASONS_BY_SPECIES[title]["dog"])
        return st.selectbox("Reason", species_options, key=f"{key_prefix}_reason_select_{title}")

    if title in VETERINARY_TASK_REASONS:
        return st.selectbox("Reason", VETERINARY_TASK_REASONS[title], key=f"{key_prefix}_reason_select_{title}")

    return None


def render_dog_cafe_menu_picker() -> str:
    section_index = st.selectbox(
        "Menu", range(len(A_LA_BARK_MENU)), format_func=lambda i: A_LA_BARK_MENU[i][0], key="dog_cafe_menu_section"
    )
    section_name, tagline, items = A_LA_BARK_MENU[section_index]
    item_labels = [f"{name} ({price})" for name, price, _ in items]
    item_index = st.selectbox(
        "Menu Item", range(len(items)), format_func=lambda i: item_labels[i], key=f"dog_cafe_menu_item_{section_index}"
    )
    st.caption(items[item_index][2])
    return item_labels[item_index]
