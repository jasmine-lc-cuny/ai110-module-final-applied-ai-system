"""AI Pre-Diagnostic Vet Assessment: a symptom questionnaire that retrieves a
matching specialty and recommends an available doctor, then hands the choice
off to the Appointments page for booking."""

import streamlit as st

from ai_applied_prediagnostic import assess_symptoms, recommend_doctor
from app_common import get_clinic, get_owners

COMMON_SYMPTOMS = [
    "Vomiting",
    "Diarrhea",
    "Not eating / loss of appetite",
    "Lethargy / low energy",
    "Coughing",
    "Difficulty breathing",
    "Limping / favoring a leg",
    "Itching / scratching",
    "Hair loss or flaky skin",
    "Bad breath / mouth pain",
    "Eye discharge or redness",
    "New lump or growth",
    "Wobbly / uncoordinated",
    "Behavior change / acting strange",
    "Seizure / collapse",
    "Heavy bleeding",
]

ONSET_OPTIONS = ["Today", "1-2 days ago", "3-7 days ago", "More than a week ago"]

owners = get_owners()
clinic = get_clinic()

st.title("🤖 AI Pre-Diagnostic Vet Assessment")
st.caption(
    "Answer a few questions about your pet's symptoms and the AI will suggest a matching "
    "specialty and an available doctor. This is not a diagnosis — if your pet is having a "
    "true emergency, contact an emergency vet immediately instead of waiting for this form."
)

patient_pairs = [(owner, pet) for owner in owners for pet in owner.pets]
if not patient_pairs:
    st.warning("No patients yet.")
    st.page_link("pages/patients.py", label="Go to Patients", icon="🧾")
    st.stop()

patient_index = st.selectbox(
    "Patient*",
    range(len(patient_pairs)),
    format_func=lambda i: f"{patient_pairs[i][1].name} — owned by {patient_pairs[i][0].name}",
    key="prediagnostic_patient_select",
)

with st.form("prediagnostic_assessment_form"):
    selected_symptoms = st.multiselect("What symptoms is your pet showing?", COMMON_SYMPTOMS)
    onset = st.selectbox("When did this start?", ONSET_OPTIONS)
    details = st.text_area("Anything else? How did it happen, and any other details?")
    submitted = st.form_submit_button("Run AI Assessment")

if submitted:
    if not selected_symptoms and not details.strip():
        st.info("Select at least one symptom or describe what's going on to run the assessment.")
        st.stop()

    symptom_text = ", ".join(selected_symptoms) + ". " + details
    assessment = assess_symptoms(symptom_text)
    recommendation = recommend_doctor(assessment, clinic)

    if assessment.urgency == "emergency":
        st.error(f"🚨 {assessment.explanation} {assessment.guardrail}")
    elif assessment.urgency == "urgent":
        st.warning(f"⚠️ {assessment.explanation} {assessment.guardrail}")
    else:
        st.info(f"{assessment.explanation} {assessment.guardrail}")

    st.markdown(f"**Suggested specialty:** {assessment.department} (confidence {assessment.confidence:.2f})")

    if recommendation.success:
        pet_name = patient_pairs[patient_index][1].name
        st.success(
            f"**Recommended doctor:** {recommendation.doctor.full_name} "
            f"({recommendation.doctor.specialization}) — next opening today at "
            f"{recommendation.slot_start} for {pet_name}."
        )
        st.session_state["prediagnostic_recommended_doctor_username"] = recommendation.doctor.username
        st.session_state["prediagnostic_reason_text"] = symptom_text.strip()
        st.page_link("pages/appointments.py", label="Go to Appointments to book", icon="📋")
    else:
        st.warning("No doctor with an open slot today matched this assessment — try the Appointments page directly.")
        st.session_state["prediagnostic_reason_text"] = symptom_text.strip()
        st.page_link("pages/appointments.py", label="Go to Appointments to book", icon="📋")

    with st.expander("Show assessment reasoning trace"):
        for step in recommendation.trace:
            st.markdown(f"- **{step.action}**: {step.detail}")
