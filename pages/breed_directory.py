"""Breed Directory: a searchable, filterable reference table covering every
dog and cat breed in the clinic's roster, with personality traits.

Unlike the rest of the app's plain-dict data model, this page uses pandas
for the table since it's a browse/reference tool (filter + sort over a
flat table) rather than clinic operational state that needs to round-trip
through data.json.
"""

import pandas as pd
import streamlit as st

from app_common import render_live_clock
from breed_personality import CAT_BREED_GROUPS, CAT_BREED_PERSONALITIES, DOG_BREED_GROUPS, DOG_BREED_PERSONALITIES

st.title("📖 Breed Directory")
st.caption("Personality traits for every dog and cat breed in the clinic's roster.")
render_live_clock("Breed Directory")

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
    search_query = st.text_input("Search Breed Name", "", key="breed_directory_search")

filtered_df = breed_df
if selected_type != "All":
    filtered_df = filtered_df[filtered_df["Type"] == selected_type]
if selected_category != "All":
    filtered_df = filtered_df[filtered_df["Category"] == selected_category]
if search_query:
    filtered_df = filtered_df[filtered_df["Breed"].str.contains(search_query, case=False, na=False)]

st.subheader(f"Results ({len(filtered_df)} matches found)")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)
