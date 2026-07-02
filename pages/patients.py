import streamlit as st

from pawpal_system import Owner, Pet, pet_species_icon
from app_common import NEW_OWNER_CHOICE, get_owners, save_owners

owners = get_owners()

st.title("🧾 Patients")
st.caption("Register new patients (pets and their owners) and search existing ones.")

st.subheader("Register New Patient")

# Outside the form so choosing "+ Add new owner" immediately reveals the
# "New owner name" field below — same reveal trick used for "Other (custom)"
# task titles elsewhere in the app, since widgets inside st.form don't
# trigger a rerun until the whole form is submitted.
owner_choice = st.selectbox(
    "Owner",
    list(range(len(owners))) + [NEW_OWNER_CHOICE],
    format_func=lambda option: owners[option].name if isinstance(option, int) else option,
    key="patient_owner_choice",
)
new_owner_name = (
    st.text_input("New owner name", key="patient_new_owner_name")
    if owner_choice == NEW_OWNER_CHOICE
    else None
)

with st.form("register_patient_form", clear_on_submit=True):
    st.markdown("**Owner contact info**")
    contact_cols = st.columns(3)
    existing_owner = owners[owner_choice] if isinstance(owner_choice, int) else None
    with contact_cols[0]:
        owner_phone = st.text_input("Phone", value=(existing_owner.phone or "") if existing_owner else "")
    with contact_cols[1]:
        owner_email = st.text_input("Email", value=(existing_owner.email or "") if existing_owner else "")
    with contact_cols[2]:
        owner_address = st.text_input(
            "Address", value=(existing_owner.address or "") if existing_owner else ""
        )

    st.markdown("**Pet info**")
    pet_cols = st.columns(4)
    with pet_cols[0]:
        pet_name = st.text_input("Name*")
    with pet_cols[1]:
        pet_species = st.selectbox("Species*", ["dog", "cat", "bunny", "other"])
    with pet_cols[2]:
        pet_sex = st.selectbox("Sex*", ["Female", "Male"])
    with pet_cols[3]:
        pet_age = st.number_input("Age", min_value=0, max_value=40, value=1)
    pet_blood_type = st.text_input("Blood group")
    medical_history = st.text_area("Medical history (one condition per line)")

    submitted_patient = st.form_submit_button("Save Patient")

if submitted_patient:
    owner_name = new_owner_name.strip() if owner_choice == NEW_OWNER_CHOICE else None
    if owner_choice == NEW_OWNER_CHOICE and not owner_name:
        st.error("Enter a name for the new owner.")
    elif not pet_name.strip():
        st.error("Pet name is required.")
    else:
        if owner_choice == NEW_OWNER_CHOICE:
            target_owner = Owner(owner_name)
            owners.append(target_owner)
        else:
            target_owner = owners[owner_choice]
        target_owner.phone = owner_phone.strip() or None
        target_owner.email = owner_email.strip() or None
        target_owner.address = owner_address.strip() or None
        target_owner.add_pet(
            Pet(
                name=pet_name.strip(),
                species=pet_species,
                age=int(pet_age),
                sex=pet_sex,
                blood_type=pet_blood_type.strip() or None,
                chronic_conditions=[
                    line.strip() for line in medical_history.splitlines() if line.strip()
                ],
            )
        )
        save_owners(owners)
        st.success(f"Registered {pet_name.strip()} under {target_owner.name}.")
        st.rerun()

st.divider()
st.subheader("Patients List")
search_query = st.text_input("Search by pet or owner name")

all_patients = [(owner, pet) for owner in owners for pet in owner.pets]
if search_query.strip():
    query_lower = search_query.strip().lower()
    all_patients = [
        (owner, pet)
        for owner, pet in all_patients
        if query_lower in pet.name.lower() or query_lower in owner.name.lower()
    ]

if all_patients:
    for index, (owner, pet) in enumerate(all_patients):
        with st.expander(f"{pet_species_icon(pet.species)} {pet.name} — owned by {owner.name}"):
            info_cols = st.columns(4)
            info_cols[0].metric("Species", pet.species)
            info_cols[1].metric("Sex", pet.sex or "—")
            info_cols[2].metric("Age", pet.age if pet.age is not None else "—")
            info_cols[3].metric("Blood group", pet.blood_type or "—")
            st.write(f"**Weight:** {pet.weight or '—'}")
            st.write(f"**Owner phone:** {owner.phone or '—'}")
            st.write(f"**Owner email:** {owner.email or '—'}")
            st.write(f"**Owner address:** {owner.address or '—'}")
            if pet.chronic_conditions:
                st.write("**Medical history:**")
                for entry in pet.chronic_conditions:
                    st.markdown(f"- {entry}")
            else:
                st.write("**Medical history:** —")
else:
    st.info("No patients found.")

save_owners(owners)
st.caption("Data is auto-saved to `data.json` after every change, so it persists between app runs.")
