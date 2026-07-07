"""Adoption Match Quiz: a short lifestyle questionnaire that scores every
seeded breed against the answers (ai_applied_adoption_match.py) and shows
the top 5 ranked matches with a plain-language "Good match / Caution / Not
ideal" label and a per-breed scoring trace.
"""

import streamlit as st

from ai_applied_adoption_match import QuizAnswers, best_matches
from app_common import render_live_clock
from mock_shelter_listings import DEMO_LISTINGS_CAPTION, mock_available_pets
from pawpal_system import pet_species_icon
from ui_helpers import render_page_banner

render_page_banner("pet_adoption")
st.title("🧭 Adoption Match Quiz")
st.caption("Answer a few questions and we'll rank the breeds that best fit your lifestyle.")
render_live_clock("Adoption Match Quiz")

st.session_state.setdefault("favorite_breeds", [])

with st.form("adoption_quiz_form"):
    species_choice = st.radio("Which are you open to?", ["No preference", "Dog", "Cat"], horizontal=True, key="quiz_species")
    energy_choice = st.radio(
        "What energy level do you want?",
        ["Low (calm, low-key)", "Medium (moderate activity)", "High (very active)"],
        key="quiz_energy",
    )
    grooming_choice = st.radio(
        "How much grooming upkeep are you willing to do?",
        ["Low (minimal)", "Medium (regular brushing)", "High (frequent grooming, happy to do it)"],
        key="quiz_grooming",
    )
    apartment_choice = st.radio("Where do you live?", ["Apartment / small space", "House with a yard"], key="quiz_apartment")
    kid_choice = st.checkbox("Must be good with kids", key="quiz_kids")
    submitted = st.form_submit_button("Find My Match")

if submitted:
    species_map = {"No preference": "either", "Dog": "dog", "Cat": "cat"}
    tier_map = {"Low (calm, low-key)": "low", "Medium (moderate activity)": "medium", "High (very active)": "high"}
    grooming_map = {"Low (minimal)": "low", "Medium (regular brushing)": "medium", "High (frequent grooming, happy to do it)": "high"}

    answers = QuizAnswers(
        species_preference=species_map[species_choice],
        energy_level=tier_map[energy_choice],
        grooming_tolerance=grooming_map[grooming_choice],
        apartment=(apartment_choice == "Apartment / small space"),
        wants_kid_friendly=kid_choice,
    )
    st.session_state["adoption_quiz_results"] = best_matches(answers, top_n=5)

results = st.session_state.get("adoption_quiz_results")
if results:
    st.subheader("🏆 Best For You")
    for match in results:
        with st.container(border=True):
            header_col, label_col = st.columns([3, 1])
            with header_col:
                st.markdown(f"### {pet_species_icon(match.species)} {match.breed}")
            with label_col:
                if match.score >= 3:
                    st.success(f"{match.label} ({match.score}/{match.max_score})")
                elif match.score == 2:
                    st.warning(f"{match.label} ({match.score}/{match.max_score})")
                else:
                    st.error(f"{match.label} ({match.score}/{match.max_score})")

            st.write(match.personality)

            with st.expander("Show match reasoning"):
                for line in match.trace:
                    st.markdown(f"- {line}")

            st.write("**Available now (demo):**")
            for pet in mock_available_pets(match.species, match.breed):
                st.markdown(f"- **{pet['name']}** ({pet['age']} yrs) — {pet['blurb']}")
            st.caption(DEMO_LISTINGS_CAPTION)

            key = f"{match.species}|{match.breed}"
            is_favorite = key in st.session_state["favorite_breeds"]
            if st.button("★ Remove from Favorites" if is_favorite else "☆ Add to Favorites", key=f"quiz_fav_{key}"):
                if is_favorite:
                    st.session_state["favorite_breeds"].remove(key)
                else:
                    st.session_state["favorite_breeds"].append(key)
                st.rerun()
else:
    st.info("Fill out the quiz above to see your top 5 breed matches.")
