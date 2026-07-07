"""PawPal AI Pet Adoption: a breed-personality browser to help a prospective
adopter find a dog or cat breed that matches the temperament they want.

Uses the same breed_personality.py lookup table as the Breed Directory page,
just themed and filtered for the adoption use case (its own nav section,
per the user's request, rather than folded into Breed Directory).
"""

import pandas as pd
import streamlit as st

from app_common import render_live_clock
from breed_personality import CAT_BREED_GROUPS, CAT_BREED_PERSONALITIES, DOG_BREED_GROUPS, DOG_BREED_PERSONALITIES
from ui_helpers import render_page_banner

render_page_banner("pet_adoption")
st.title("🐾 PawPal AI Pet Adoption")
st.caption("Browse dog and cat breeds by personality to find your best match.")
render_live_clock("PawPal AI Pet Adoption")

rows = []
for group_name, breeds in DOG_BREED_GROUPS.items():
    for breed in breeds:
        rows.append({"Type": "Dog", "Category": group_name, "Breed": breed, "Personality": DOG_BREED_PERSONALITIES[breed]})
for group_name, breeds in CAT_BREED_GROUPS.items():
    for breed in breeds:
        rows.append({"Type": "Cat", "Category": group_name, "Breed": breed, "Personality": CAT_BREED_PERSONALITIES[breed]})

breed_df = pd.DataFrame(rows)

st.subheader("🔍 Find Your Match")
selected_type = st.radio("Pet Type", ["All", "Dog", "Cat"], horizontal=True, key="pet_adoption_type_filter")

if selected_type != "All":
    available_categories = ["All"] + sorted(breed_df[breed_df["Type"] == selected_type]["Category"].unique())
else:
    available_categories = ["All"] + sorted(breed_df["Category"].unique())

filter_cols = st.columns(2)
with filter_cols[0]:
    selected_category = st.selectbox("Breed Group", available_categories, key="pet_adoption_category_filter")
with filter_cols[1]:
    search_query = st.text_input("Search by trait or breed (e.g. 'gentle', 'Poodle')", "", key="pet_adoption_search")

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

st.subheader(f"Matches ({len(filtered_df)})")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)
