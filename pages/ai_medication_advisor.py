"""AI Medication Advisor: given a diagnosed condition, recommend a curated
medication whose real labeled indication matches it, strictly from
data/medication_guides.csv - never a dose, and never a species-inappropriate
suggestion."""

import streamlit as st

from ai_applied_medication_advisor import recommend_medication
from app_common import get_owners

COMMON_CONDITIONS = [
    "Osteoarthritis / joint pain",
    "Allergic or atopic dermatitis (itching)",
    "Gastric ulcer / acid reflux",
    "Vomiting / nausea",
    "Diarrhea / Giardia",
    "Congestive heart failure",
    "Seizures / epilepsy",
    "Bacterial skin infection",
    "Urinary tract infection",
    "Heartworm prevention",
    "Flea / tick infestation",
    "Intestinal parasites (tapeworm, roundworm, hookworm)",
    "Separation anxiety / situational anxiety",
    "Hyperthyroidism",
    "Cushing's disease",
    "Diabetes mellitus",
]

st.title("💊 AI Medication Advisor")
st.caption(
    "Enter a pet's diagnosed condition and the AI will recommend a medication from a small, curated "
    "reference, strictly based on each medication's real labeled indication. This never includes a "
    "dose and never replaces your veterinarian's prescription and judgment."
)

owners = get_owners()
patient_pairs = [(owner, pet) for owner in owners for pet in owner.pets]
if not patient_pairs:
    st.warning("No patients yet.")
    st.page_link("pages/patients.py", label="Go to Patients", icon="🧾")
    st.stop()

patient_index = st.selectbox(
    "Patient*",
    range(len(patient_pairs)),
    format_func=lambda i: f"{patient_pairs[i][1].name} — owned by {patient_pairs[i][0].name}",
    key="medication_patient_select",
)
species = patient_pairs[patient_index][1].species

with st.form("medication_advisor_form"):
    condition_pick = st.selectbox("Diagnosed condition", ["(choose one)"] + COMMON_CONDITIONS)
    condition_details = st.text_area("Or describe the diagnosed condition in your own words")
    submitted = st.form_submit_button("Get Medication Recommendation")

if submitted:
    condition_text = condition_details.strip()
    if condition_pick != "(choose one)":
        condition_text = f"{condition_pick}. {condition_text}".strip()

    if not condition_text:
        st.info("Choose a condition or describe it to get a recommendation.")
        st.stop()

    recommendation = recommend_medication(condition_text, species)

    if recommendation.medication is None:
        st.warning(recommendation.explanation)
    else:
        st.success(f"**Recommended medication:** {recommendation.medication} (confidence {recommendation.confidence:.2f})")
        st.markdown(f"**Label status:** {recommendation.label_status}")
        st.info(recommendation.indication)
        st.warning(f"⚠️ {recommendation.guardrail}")

    st.caption(
        "This is a small, curated reference covering common conditions, not a full formulary, and it "
        "never states a dose. Final medication choice and dosage must be confirmed by a licensed "
        "veterinarian using the actual product label."
    )
