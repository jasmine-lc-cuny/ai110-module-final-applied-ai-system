"""Realistic grooming-visit duration estimation.

Maps a dog's breed (or, when the breed isn't recognized, its weight) to a
size tier, and a size tier to a realistic full-service grooming duration
range (bath, dry, haircut, nails, ears) — based on typical professional
grooming times, which scale heavily with a dog's size and coat. Cats get a
single shorter range regardless of breed, since grooming-time variance by
cat breed is much smaller than for dogs.
"""

from __future__ import annotations

import random
import re

DOG_BREED_SIZE_TIERS = {
    "Chihuahua": "small",
    "Yorkshire Terrier": "small",
    "Shih Tzu": "small",
    "Dachshund": "small",
    "Beagle": "medium",
    "French Bulldog": "medium",
    "Bulldog": "medium",
    "Border Collie": "medium",
    "Pembroke Welsh Corgi": "medium",
    "Australian Shepherd": "medium",
    "Labrador Retriever": "large",
    "Golden Retriever": "large",
    "German Shepherd": "large",
    "Boxer": "large",
    "Siberian Husky": "large",
    "Rottweiler": "large",
    "Poodle": "large",
    "Pit Bull Terrier": "large",
    "Great Dane": "giant",
}

# Fallback for dogs whose breed isn't in the table above (e.g. a custom
# breed typed into the patient registration form): bucket by weight instead.
# Each threshold is the upper bound (in lbs) for that tier.
WEIGHT_SIZE_THRESHOLDS = [
    (20, "small"),
    (50, "medium"),
    (90, "large"),
]

DOG_GROOMING_DURATION_RANGES = {
    "small": (60, 120),
    "medium": (90, 180),
    "large": (120, 180),
    "giant": (180, 240),
}
CAT_GROOMING_DURATION_RANGE = (30, 60)

DEFAULT_DOG_SIZE_TIER = "medium"


def _parse_weight_lbs(weight_text: str | None) -> float | None:
    """Pull a leading number out of a free-text weight field like '45 lbs'."""
    if not weight_text:
        return None
    match = re.search(r"[\d.]+", weight_text)
    if not match:
        return None
    return float(match.group())


def dog_size_tier(breed: str | None, weight: str | None = None) -> str:
    """Determine a dog's size tier by breed name, falling back to weight,
    falling back to "medium" if neither is available or recognized."""
    if breed and breed in DOG_BREED_SIZE_TIERS:
        return DOG_BREED_SIZE_TIERS[breed]

    pounds = _parse_weight_lbs(weight)
    if pounds is not None:
        for threshold, tier in WEIGHT_SIZE_THRESHOLDS:
            if pounds <= threshold:
                return tier
        return "giant"

    return DEFAULT_DOG_SIZE_TIER


def grooming_duration_minutes(species: str, breed: str | None = None, weight: str | None = None) -> int:
    """A realistic full-service grooming visit length in minutes, randomized
    within a size-appropriate range."""
    if species.lower() == "cat":
        low, high = CAT_GROOMING_DURATION_RANGE
    else:
        tier = dog_size_tier(breed, weight)
        low, high = DOG_GROOMING_DURATION_RANGES[tier]
    return random.randint(low, high)
