"""Breed Directory: a searchable, filterable reference table covering every
dog and cat breed in the clinic's roster, with personality traits and
lifestyle filters, plus a per-breed detail dialog (temperament, exercise,
grooming, health notes, mock 'available now' listings) and buttons to add
a breed to Favorites or the Compare Breeds selection.

Lives under the "PawPal AI Pet Adoption" nav section (its own top-level
section, per the user's request) and uses the same breed_personality.py /
breed_traits.py lookup tables as the other adoption pages.
"""

import pandas as pd
import streamlit as st

from app_common import render_live_clock
from breed_personality import CAT_BREED_GROUPS, CAT_BREED_PERSONALITIES, DOG_BREED_GROUPS, DOG_BREED_PERSONALITIES, breed_personality
from breed_traits import breed_traits, exercise_needs_text
from mock_shelter_listings import DEMO_LISTINGS_CAPTION, mock_available_pets
from seed.seed_animals_distribution import BREED_ALWAYS_HAS, CAT_BREED_RISKS, DOG_BREED_RISKS
from ui_helpers import render_page_banner

render_page_banner("pet_adoption")
st.title("📖 Breed Directory")
st.caption("Browse dog and cat breeds by personality traits to find your match.")
render_live_clock("Breed Directory")

st.session_state.setdefault("favorite_breeds", [])
st.session_state.setdefault("compare_breeds", [])

rows = []
for group_name, breeds in DOG_BREED_GROUPS.items():
    for breed in breeds:
        rows.append({"Type": "Dog", "Category": group_name, "Breed": breed, "Personality": DOG_BREED_PERSONALITIES[breed]})
for group_name, breeds in CAT_BREED_GROUPS.items():
    for breed in breeds:
        rows.append({"Type": "Cat", "Category": group_name, "Breed": breed, "Personality": CAT_BREED_PERSONALITIES[breed]})

breed_df = pd.DataFrame(rows)

st.subheader("🔍 Filters")
selected_type = st.radio("Pet Type", ["All", "Dog", "Cat"], horizontal=True, key="breed_directory_type_filter")

if selected_type != "All":
    available_categories = ["All"] + sorted(breed_df[breed_df["Type"] == selected_type]["Category"].unique())
else:
    available_categories = ["All"] + sorted(breed_df["Category"].unique())

filter_cols = st.columns(2)
with filter_cols[0]:
    selected_category = st.selectbox("Breed Group", available_categories, key="breed_directory_category_filter")
with filter_cols[1]:
    search_query = st.text_input("Search by trait or breed (e.g. 'gentle', 'Poodle')", "", key="breed_directory_search")

lifestyle_options = ["Apartment-friendly", "Low-shedding", "Beginner-friendly", "Active", "Calm", "Hypoallergenic", "Family-friendly"]
lifestyle_filters = st.multiselect("Lifestyle filters", lifestyle_options, key="breed_directory_lifestyle_filters")

filtered_df = breed_df
if selected_type != "All":
    filtered_df = filtered_df[filtered_df["Type"] == selected_type]
if selected_category != "All":
    filtered_df = filtered_df[filtered_df["Category"] == selected_category]
if search_query:
    query_lower = search_query.strip().lower()
    filtered_df = filtered_df[
        filtered_df["Breed"].str.lower().str.contains(query_lower, na=False)
        | filtered_df["Personality"].str.lower().str.contains(query_lower, na=False)
    ]

if lifestyle_filters:
    def passes_lifestyle(row) -> bool:
        traits = breed_traits(row["Type"].lower(), row["Breed"])
        if traits is None:
            return False
        checks = {
            "Apartment-friendly": traits.apartment_friendly,
            "Low-shedding": traits.shedding_level == "low",
            "Beginner-friendly": traits.beginner_friendly,
            "Active": traits.energy_level == "high",
            "Calm": traits.energy_level == "low",
            "Hypoallergenic": traits.hypoallergenic,
            "Family-friendly": traits.kid_friendly,
        }
        return all(checks[option] for option in lifestyle_filters)

    filtered_df = filtered_df[filtered_df.apply(passes_lifestyle, axis=1)]

st.subheader(f"Matches ({len(filtered_df)})")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)


@st.dialog("Breed Detail")
def breed_detail_dialog(species: str, breed: str) -> None:
    traits = breed_traits(species, breed)
    st.subheader(breed)
    st.write(f"**Temperament:** {breed_personality(species, breed) or '—'}")
    st.write(f"**Exercise needs:** {exercise_needs_text(traits)}")
    st.write(f"**Grooming needs:** {traits.grooming_needs.capitalize()}  |  **Shedding:** {traits.shedding_level.capitalize()}")

    badges = []
    if traits.apartment_friendly:
        badges.append("🏢 Apartment-friendly")
    if traits.hypoallergenic:
        badges.append("🤧 Hypoallergenic")
    if traits.kid_friendly:
        badges.append("👶 Family-friendly")
    if traits.beginner_friendly:
        badges.append("🌱 Beginner-friendly")
    if badges:
        st.write(" · ".join(badges))

    risks = (DOG_BREED_RISKS if species == "dog" else CAT_BREED_RISKS).get(breed, [])
    st.write("**Common health notes:**")
    if breed in BREED_ALWAYS_HAS:
        st.markdown(f"- {BREED_ALWAYS_HAS[breed]}")
    if risks:
        for risk in risks:
            st.markdown(f"- {risk}")
    elif breed not in BREED_ALWAYS_HAS:
        st.write(f"None specifically identified for the {breed} breed.")

    st.divider()
    st.write("**Available now (demo):**")
    for pet in mock_available_pets(species, breed):
        st.markdown(f"- **{pet['name']}** ({pet['age']} yrs) — {pet['blurb']}")
    st.caption(DEMO_LISTINGS_CAPTION)


st.divider()
st.subheader("View, favorite, or compare a breed")
detail_options = [f"{row.Type} — {row.Breed}" for row in filtered_df.itertuples()]
if detail_options:
    picked = st.selectbox("Pick a breed", detail_options, key="breed_directory_detail_pick")
    picked_type, picked_breed = picked.split(" — ", 1)
    picked_species = picked_type.lower()
    picked_key = f"{picked_species}|{picked_breed}"
    is_favorite = picked_key in st.session_state["favorite_breeds"]
    in_compare = picked_key in st.session_state["compare_breeds"]
    compare_full = len(st.session_state["compare_breeds"]) >= 3

    # These are plain top-level buttons (not inside the dialog) so favoriting
    # or adding to compare doesn't require the dialog to stay open across a
    # rerun — st.dialog closes on any rerun triggered from within it.
    detail_col, fav_col, compare_col = st.columns(3)
    with detail_col:
        if st.button("🔍 View Detail", key="breed_directory_view_detail"):
            breed_detail_dialog(picked_species, picked_breed)
    with fav_col:
        if st.button("★ Remove from Favorites" if is_favorite else "☆ Add to Favorites", key="breed_directory_toggle_favorite"):
            if is_favorite:
                st.session_state["favorite_breeds"].remove(picked_key)
            else:
                st.session_state["favorite_breeds"].append(picked_key)
            st.rerun()
    with compare_col:
        if st.button("➖ Remove from Compare" if in_compare else "➕ Add to Compare", key="breed_directory_toggle_compare", disabled=(compare_full and not in_compare)):
            if in_compare:
                st.session_state["compare_breeds"].remove(picked_key)
            else:
                st.session_state["compare_breeds"].append(picked_key)
            st.rerun()
else:
    st.info("No breeds match the current filters.")
