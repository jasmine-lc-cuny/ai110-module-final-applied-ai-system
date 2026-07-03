from collections import Counter, defaultdict
from datetime import date

import pandas as pd
import streamlit as st

from pawpal_system import format_time_12h, pet_species_icon, task_type_icon
from app_common import get_owners

VET_ICONS = {"🏥", "💊"}
PATIENTS_PER_PAGE = 8


def render_info_card(owner, pet) -> None:
    """Render the mockup's "Info" card: identity basics plus the owner."""
    with st.container(border=True):
        st.markdown("**Info**")
        st.write(f"**Name:** {pet.name}")
        st.write(f"**Owner:** {owner.name}")
        st.write(f"**Breed:** {pet.breed or '—'}")
        st.write(f"**Weight:** {pet.weight or '—'}")
        st.write(f"**Sex:** {pet.sex or '—'}")
        st.write(f"**Age:** {pet.age if pet.age is not None else '—'}")
        st.write(f"**Status:** {pet.status}")


def render_visit_statistics_card(pet) -> None:
    """Render the monthly completed-vet-visit line chart card."""
    with st.container(border=True):
        st.markdown("**📈 Visit statistics**")
        monthly_counts = defaultdict(int)
        for task in pet.tasks:
            if task.completed and task_type_icon(task.title) in VET_ICONS:
                monthly_counts[date(task.due_date.year, task.due_date.month, 1)] += 1
        if monthly_counts:
            sorted_months = sorted(monthly_counts.keys())
            chart_data = pd.DataFrame(
                {"Vet visits": [monthly_counts[month] for month in sorted_months]},
                index=[month.strftime("%b %Y") for month in sorted_months],
            )
            st.line_chart(chart_data)
        else:
            st.info("No completed vet visits yet.")


def render_diet_card(pet) -> None:
    """Render the mockup's "Diet" card: should/should-not bullet lists."""
    with st.container(border=True):
        st.markdown("**Diet**")
        st.markdown("✅ **The diet should contain:**")
        if pet.diet_good:
            for item in pet.diet_good:
                st.markdown(f"- {item}")
        else:
            st.caption("Not set yet.")
        st.markdown("❌ **The diet should not contain:**")
        if pet.diet_bad:
            for item in pet.diet_bad:
                st.markdown(f"- {item}")
        else:
            st.caption("Not set yet.")


def render_chronic_card(pet) -> None:
    """Render the chronic-conditions card, bolding each condition's name."""
    with st.container(border=True):
        st.markdown("**🩺 Chronic diseases**")
        if pet.chronic_conditions:
            for entry in pet.chronic_conditions:
                name, separator, note = entry.partition(":")
                if separator:
                    st.markdown(f"- **{name.strip()}**: {note.strip()}")
                else:
                    st.markdown(f"- {entry.strip()}")
        else:
            st.caption("No chronic conditions on file.")


def render_appointment_reason_card(pet) -> None:
    """Render the appointment-reason card from the most relevant task notes."""
    with st.container(border=True):
        st.markdown("**🐾 Appointment Reason**")
        today = date.today()
        upcoming_with_notes = [t for t in pet.tasks if t.notes and t.due_date >= today]
        past_with_notes = [t for t in pet.tasks if t.notes and t.due_date < today]
        if upcoming_with_notes:
            reason_task = min(upcoming_with_notes, key=lambda t: (t.due_date, t.time))
        elif past_with_notes:
            reason_task = max(past_with_notes, key=lambda t: (t.due_date, t.time))
        else:
            reason_task = None
        if reason_task:
            st.write(reason_task.notes)
        else:
            st.caption("No notes yet.")


owners = get_owners()
pet_pairs = [(owner, pet) for owner in owners for pet in owner.pets]

st.title("📊 Dashboard")
st.caption("A per-patient clinical overview across every owner.")

if not pet_pairs:
    st.info("Add a pet to see their dashboard here.")
    st.page_link("pages/patients.py", label="Go to Patients", icon="🧾")
else:
    # Pill-style patient switcher (like the mockup's Tortilla/Noodle/Charlie
    # bar), paginated so a large roster shows one row at a time. Duplicate
    # pet names across different owners get the owner's name appended so two
    # pills never look identical.
    name_counts = Counter(pet.name for _, pet in pet_pairs)

    def pill_label(index: int) -> str:
        owner, pet = pet_pairs[index]
        label = f"{pet_species_icon(pet.species)} {pet.name}"
        if name_counts[pet.name] > 1:
            label += f" · {owner.name}"
        return label

    if "dashboard_selected_pet" not in st.session_state:
        st.session_state.dashboard_selected_pet = 0
    if "dashboard_pill_page" not in st.session_state:
        st.session_state.dashboard_pill_page = 0

    total_pages = (len(pet_pairs) + PATIENTS_PER_PAGE - 1) // PATIENTS_PER_PAGE
    pill_page = min(st.session_state.dashboard_pill_page, total_pages - 1)
    page_start = pill_page * PATIENTS_PER_PAGE
    page_options = list(range(page_start, min(page_start + PATIENTS_PER_PAGE, len(pet_pairs))))
    # Each page gets its own widget key: reusing one key while the options
    # list changes underneath it would leave a stale (now-invalid) value in
    # session state and crash the pills widget on rerun.
    page_pills_key = f"dashboard_pet_pills_{pill_page}"

    def _select_pet_from_pills() -> None:
        # on_change only fires on a real click (never on rerender), so this
        # can't clobber a selection made on a different page the way an
        # inline "if value != selection" sync would.
        picked = st.session_state.get(page_pills_key)
        if picked is not None:
            st.session_state.dashboard_selected_pet = picked

    nav_prev, nav_label, nav_next = st.columns([1, 6, 1])
    with nav_prev:
        if st.button("◀", key="pill_page_prev", disabled=pill_page == 0):
            new_page = pill_page - 1
            st.session_state.dashboard_pill_page = new_page
            # Drop the destination page's old widget state so its pills
            # re-render highlighting the current selection (or nothing),
            # instead of a stale pick from an earlier visit.
            st.session_state.pop(f"dashboard_pet_pills_{new_page}", None)
            st.rerun()
    with nav_label:
        default_on_page = (
            st.session_state.dashboard_selected_pet
            if st.session_state.dashboard_selected_pet in page_options
            else None
        )
        st.pills(
            "Patient",
            page_options,
            format_func=pill_label,
            default=default_on_page,
            key=page_pills_key,
            on_change=_select_pet_from_pills,
            label_visibility="collapsed",
        )
        st.caption(f"Patients {page_start + 1}–{page_options[-1] + 1} of {len(pet_pairs)}")
    with nav_next:
        if st.button("▶", key="pill_page_next", disabled=pill_page >= total_pages - 1):
            new_page = pill_page + 1
            st.session_state.dashboard_pill_page = new_page
            st.session_state.pop(f"dashboard_pet_pills_{new_page}", None)
            st.rerun()

    selected_index = min(st.session_state.dashboard_selected_pet, len(pet_pairs) - 1)
    selected_owner, selected_pet = pet_pairs[selected_index]

    top_row = st.columns(3)
    with top_row[0]:
        render_info_card(selected_owner, selected_pet)
    with top_row[1]:
        render_visit_statistics_card(selected_pet)
    with top_row[2]:
        render_diet_card(selected_pet)

    middle_row = st.columns(2)
    with middle_row[0]:
        render_chronic_card(selected_pet)
    with middle_row[1]:
        render_appointment_reason_card(selected_pet)

    st.divider()
    with st.container(border=True):
        today = date.today()
        all_task_triples = [
            (owner, pet, task)
            for owner, pet in pet_pairs
            for task in pet.tasks
        ]
        open_today = [
            triple for triple in all_task_triples
            if triple[2].due_date == today and not triple[2].completed
        ]
        st.markdown("**Today**")
        st.metric("Appointments", len(open_today))

        st.markdown("**Upcoming Appointments**")
        upcoming = sorted(
            (
                triple for triple in all_task_triples
                if triple[2].due_date >= today and not triple[2].completed
            ),
            key=lambda triple: (triple[2].due_date, triple[2].time),
        )[:5]
        if upcoming:
            for upcoming_owner, upcoming_pet, upcoming_task in upcoming:
                st.write(
                    f"{task_type_icon(upcoming_task.title)} {upcoming_pet.name} — "
                    f"{upcoming_task.title} ({format_time_12h(upcoming_task.time)}, "
                    f"{upcoming_task.due_date.isoformat()})"
                )
        else:
            st.caption("No upcoming appointments.")

# ==========================================
# 📊 CATEGORIZED PATIENTS DIRECTORY (TABS)
# ==========================================
st.divider()
st.subheader("Patients Directory")

PET_CATEGORIES = {
    "🐶 General Companion": ["dog", "cat"],
    "🐹 Exotic Small Pet": ["rabbit", "bunny", "hamster", "gerbil", "mouse", "mice", "rat", "chinchilla", "guinea pig", "ferret", "hedgehog", "sugar glider", "squirrel"],
    "🦜 Exotic Avian": ["budgie", "canary", "finch", "parrot", "cockatiel", "conure", "chicken", "duck", "goose", "pigeon", "owl", "falcon", "snowy owl"],
    "🦎 Reptiles & Amphibians": ["bearded dragon", "leopard gecko", "crested gecko", "chameleon", "iguana", "skink", "turtle", "tortoise", "corn snake", "ball python", "king snake", "frog", "toad", "newt", "salamander"],
    "🐠 Fish & Invertebrates": ["betta", "guppy", "platy", "swordtail", "molly", "tetra", "goldfish", "danio", "minnow", "cichlid", "pleco", "clownfish", "damselfish", "goby", "blenny"]
}

selected_group = st.radio(
    "Filter by Species Group",
    options=list(PET_CATEGORIES.keys()),
    horizontal=True,
    key="dashboard_directory_group"
)

search_query = st.text_input("Search by pet or owner name", key="dashboard_search")

def render_patient_cards(patient_list):
    if not patient_list:
        st.info("No patients matching this sub-category.")
        return
        
    for owner, pet in patient_list:
        status_flag = "" if pet.status == "Alive" else " 🪦"
        with st.expander(f"{pet_species_icon(pet.species)} {pet.name}{status_flag} — owned by {owner.name}"):
            info_cols = st.columns(4)
            info_cols[0].metric("Species", pet.species.capitalize())
            info_cols[1].metric("Sex", pet.sex or "—")
            info_cols[2].metric("Age", pet.age if pet.age is not None else "—")
            info_cols[3].metric("Status", pet.status)
            
            st.write(f"**Breed:** {pet.breed or '—'}")
            st.write(f"**Weight:** {pet.weight or '—'}  |  **Height:** {pet.height or '—'}")
            st.write(f"**Color/Markings:** {pet.color_markings or '—'}")
            st.write(f"**Microchip #:** {pet.microchip_number or '—'}")
            st.write(f"**Spayed/Neutered:** {pet.spayed_neutered or 'Unknown'}")
            st.write(f"**Allergies:** {pet.allergies or '—'}")
            st.write(f"**Blood group:** {pet.blood_type or '—'}")
            st.write(f"**Behavioral Notes:** {pet.behavioral_notes or '—'}")
            
            if hasattr(pet, 'diet_good') and pet.diet_good:
                st.write("**Allowed Foods:**")
                for item in pet.diet_good:
                    st.markdown(f"- {item}")
            if hasattr(pet, 'diet_bad') and pet.diet_bad:
                st.write("**Prohibited Foods:**")
                for item in pet.diet_bad:
                    st.markdown(f"- :red[{item}]")
                    
            st.write(f"**Owner phone:** {owner.phone or '—'}")
            st.write(f"**Owner email:** {owner.email or '—'}")
            st.write(f"**Owner address:** {owner.address or '—'}")
            if pet.chronic_conditions:
                st.write("**Medical history:**")
                for entry in pet.chronic_conditions:
                    st.markdown(f"- {entry}")
            else:
                st.write("**Medical history:** —")

all_patients = [(owner, pet) for owner in get_owners() for pet in owner.pets]
allowed_species = PET_CATEGORIES[selected_group]
query_lower = search_query.strip().lower()

filtered_group_patients = []
for owner, pet in all_patients:
    matches_search = not query_lower or query_lower in pet.name.lower() or query_lower in owner.name.lower()
    
    if selected_group == "🐶 General Companion":
        all_known_species = [s for g in PET_CATEGORIES.values() for s in g]
        matches_species = pet.species.lower() in allowed_species or pet.species.lower() not in all_known_species
    else:
        matches_species = pet.species.lower() in allowed_species
        
    if matches_search and matches_species:
        filtered_group_patients.append((owner, pet))

if not filtered_group_patients:
    st.info("No patients currently registered under this category.")
else:
    if "General Companion" in selected_group:
        tab_titles = ["🐕 Dogs", "🐈 Cats", "🐾 Others"]
        tabs = st.tabs(tab_titles)
        with tabs[0]:
            render_patient_cards([(o, p) for o, p in filtered_group_patients if p.species.lower() == "dog"])
        with tabs[1]:
            render_patient_cards([(o, p) for o, p in filtered_group_patients if p.species.lower() == "cat"])
        with tabs[2]:
            render_patient_cards([(o, p) for o, p in filtered_group_patients if p.species.lower() not in ["dog", "cat"]])

    elif "Exotic Small Pet" in selected_group:
        tab_titles = ["🐿️ Rodents", "🦔 Special Mammals"]
        tabs = st.tabs(tab_titles)
        rodents = ["rabbit", "bunny", "hamster", "gerbil", "mouse", "mice", "rat", "chinchilla", "guinea pig"]
        with tabs[0]:
            render_patient_cards([(o, p) for o, p in filtered_group_patients if p.species.lower() in rodents])
        with tabs[1]:
            render_patient_cards([(o, p) for o, p in filtered_group_patients if p.species.lower() not in rodents])

    elif "Exotic Avian" in selected_group:
        tab_titles = ["🐤 Small Birds", "🦅 Large Birds & Raptors", "🐓 Poultry"]
        tabs = st.tabs(tab_titles)
        small_birds = ["budgie", "canary", "finch", "cockatiel"]
        poultry = ["chicken", "duck", "goose", "pigeon"]
        with tabs[0]:
            render_patient_cards([(o, p) for o, p in filtered_group_patients if p.species.lower() in small_birds])
        with tabs[1]:
            render_patient_cards([(o, p) for o, p in filtered_group_patients if p.species.lower() not in small_birds and p.species.lower() not in poultry])
        with tabs[2]:
            render_patient_cards([(o, p) for o, p in filtered_group_patients if p.species.lower() in poultry])

    elif "Reptiles & Amphibians" in selected_group:
        tab_titles = ["🦎 Lizards & Snakes", "🐢 Chelonians", "🐸 Amphibians"]
        tabs = st.tabs(tab_titles)
        snakes_lizards = ["bearded dragon", "leopard gecko", "crested gecko", "chameleon", "iguana", "skink", "corn snake", "ball python", "king snake"]
        chelonians = ["turtle", "tortoise"]
        with tabs[0]:
            render_patient_cards([(o, p) for o, p in filtered_group_patients if p.species.lower() in snakes_lizards])
        with tabs[1]:
            render_patient_cards([(o, p) for o, p in filtered_group_patients if p.species.lower() in chelonians])
        with tabs[2]:
            render_patient_cards([(o, p) for o, p in filtered_group_patients if p.species.lower() not in snakes_lizards and p.species.lower() not in chelonians])

    elif "Fish & Invertebrates" in selected_group:
        tab_titles = ["💧 Freshwater", "🌊 Saltwater"]
        tabs = st.tabs(tab_titles)
        saltwater = ["clownfish", "damselfish", "goby", "blenny"]
        with tabs[0]:
            render_patient_cards([(o, p) for o, p in filtered_group_patients if p.species.lower() not in saltwater])
        with tabs[1]:
            render_patient_cards([(o, p) for o, p in filtered_group_patients if p.species.lower() in saltwater])