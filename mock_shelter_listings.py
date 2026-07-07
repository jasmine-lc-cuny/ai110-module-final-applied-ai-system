"""Mock 'available now' shelter listings for the adoption quiz results and
breed detail views. These are clearly-labeled fictional presentation data
— never written to data.json, never confused with a real patient — used
only to make browsing feel adoption-focused rather than a bare spec sheet.

Names are chosen deterministically from the breed name (not the process
RNG) so a given breed always shows the same mock listing across reruns
instead of jittering every time Streamlit reruns the script.
"""

from __future__ import annotations

import random

from breed_personality import breed_personality
from seed.seed_animals_distribution import PET_NAMES

DEMO_LISTINGS_CAPTION = "🐾 Demo listings for illustration only — not real shelter inventory."


def mock_available_pets(species: str, breed: str, count: int = 2) -> list[dict]:
    """Return `count` deterministic fictional 'available now' listings for
    a breed: name, age, species, and a short personality blurb."""
    rng = random.Random(f"{species}:{breed}")
    names = rng.sample(PET_NAMES, count)
    personality = breed_personality(species, breed) or ""
    listings = []
    for name in names:
        listings.append(
            {
                "name": name,
                "age": rng.randint(1, 8),
                "species": species,
                "breed": breed,
                "blurb": personality,
            }
        )
    return listings
