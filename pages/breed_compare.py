"""Compare Breeds: pick 2-3 breeds and see their traits, temperament, and
health notes side by side.
"""

import streamlit as st

from app_common import render_live_clock
from breed_personality import CAT_BREED_GROUPS, DOG_BREED_GROUPS, breed_personality
from breed_traits import breed_traits, exercise_needs_text
from seed.seed_animals_distribution import BREED_ALWAYS_HAS, CAT_BREED_RISKS, DOG_BREED_RISKS
from ui_helpers import render_page_banner

render_page_banner("pet_adoption")
st.title("⚖️ Compare Breeds")
st.caption("Select 2-3 breeds to compare side by side.")
render_live_clock("Compare Breeds")

st.session_state.setdefault("compare_breeds", [])

all_options = (
    [f"Dog — {breed}" for breeds in DOG_BREED_GROUPS.values() for breed in breeds]
    + [f"Cat — {breed}" for breeds in CAT_BREED_GROUPS.values() for breed in breeds]
)

default_selection = [key.replace("dog|", "Dog — ").replace("cat|", "Cat — ") for key in st.session_state["compare_breeds"]]
default_selection = [option for option in default_selection if option in all_options]

selection = st.multiselect(
    "Choose 2-3 breeds",
    sorted(all_options),
    default=default_selection,
    max_selections=3,
    key="breed_compare_selection",
)

if len(selection) < 2:
    st.info("Pick at least 2 breeds to compare.")
else:
    columns = st.columns(len(selection))
    for col, option in zip(columns, selection):
        species_label, breed = option.split(" — ", 1)
        species = species_label.lower()
        traits = breed_traits(species, breed)
        with col:
            st.markdown(f"### {breed}")
            st.write(breed_personality(species, breed) or "—")
            st.write(f"**Energy:** {traits.energy_level.capitalize()}")
            st.write(f"**Exercise needs:** {exercise_needs_text(traits)}")
            st.write(f"**Grooming needs:** {traits.grooming_needs.capitalize()}")
            st.write(f"**Shedding:** {traits.shedding_level.capitalize()}")
            st.write(f"**Apartment-friendly:** {'Yes' if traits.apartment_friendly else 'No'}")
            st.write(f"**Kid-friendly:** {'Yes' if traits.kid_friendly else 'No'}")
            st.write(f"**Hypoallergenic:** {'Yes' if traits.hypoallergenic else 'No'}")
            st.write(f"**Beginner-friendly:** {'Yes' if traits.beginner_friendly else 'No'}")

            risks = (DOG_BREED_RISKS if species == "dog" else CAT_BREED_RISKS).get(breed, [])
            st.write("**Common health notes:**")
            if breed in BREED_ALWAYS_HAS:
                st.markdown(f"- {BREED_ALWAYS_HAS[breed]}")
            if risks:
                for risk in risks:
                    st.markdown(f"- {risk}")
            elif breed not in BREED_ALWAYS_HAS:
                st.write("None specifically identified.")
