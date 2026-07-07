"""My Adoption Plan: bookmarked breeds, a pre-adoption checklist, and a
before/first-week/first-month roadmap. All state is session-only (adoption
browsing isn't tied to an existing clinic Owner record), matching the
repo's existing pattern for page-local UI toggles.
"""

import streamlit as st

from app_common import render_live_clock
from breed_personality import breed_personality
from ui_helpers import render_page_banner

render_page_banner("pet_adoption")
st.title("📋 My Adoption Plan")
st.caption("Your favorite breeds, a pre-adoption checklist, and what to expect.")
render_live_clock("My Adoption Plan")

st.session_state.setdefault("favorite_breeds", [])

st.subheader("⭐ Favorites")
if not st.session_state["favorite_breeds"]:
    st.info("No favorites yet — add breeds from the Breed Directory or Adoption Match Quiz.")
else:
    for key in list(st.session_state["favorite_breeds"]):
        species, breed = key.split("|", 1)
        with st.container(border=True):
            cols = st.columns([4, 1])
            with cols[0]:
                st.markdown(f"**{breed}** ({species.capitalize()})")
                st.caption(breed_personality(species, breed) or "")
            with cols[1]:
                if st.button("Remove", key=f"plan_remove_fav_{key}"):
                    st.session_state["favorite_breeds"].remove(key)
                    st.rerun()

st.divider()
st.subheader("✅ Adoption Checklist")
checklist_items = ["Food", "Crate", "Leash / Carrier", "Bed", "Vet visit scheduled", "Training plan", "Documents / records"]
done_count = 0
for item in checklist_items:
    checked = st.checkbox(item, key=f"adoption_checklist_{item}")
    if checked:
        done_count += 1
st.caption(f"{done_count} / {len(checklist_items)} done")

st.divider()
st.subheader("🗓️ Adoption Timeline")
with st.expander("Before Adoption"):
    st.markdown(
        "- Pet-proof your home and pick a vet clinic\n"
        "- Buy food, a crate/carrier, bed, leash or litter box\n"
        "- Decide who handles feeding, walks, and vet visits\n"
        "- Budget for food, grooming, and routine vet care"
    )
with st.expander("First Week"):
    st.markdown(
        "- Keep the environment calm and routines simple\n"
        "- Schedule the first wellness vet visit\n"
        "- Start basic house rules and a feeding schedule\n"
        "- Watch for signs of stress and give them space to adjust"
    )
with st.expander("First Month"):
    st.markdown(
        "- Begin basic training / socialization\n"
        "- Establish a regular exercise and grooming routine\n"
        "- Schedule any follow-up vet visits or vaccinations\n"
        "- Reassess fit and reach out to your vet with any concerns"
    )
