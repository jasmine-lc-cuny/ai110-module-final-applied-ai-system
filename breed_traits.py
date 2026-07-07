"""Structured lifestyle traits per breed, used by the adoption match quiz,
the Breed Directory's lifestyle filters, and the breed compare/detail views.

Personality (breed_personality.py) is a free-text sentence; this module is
the structured counterpart — fixed enums/booleans that can be scored and
filtered on. Like breed_personality.py, traits are a property of the breed
itself, not the individual pet, so they live here as a single lookup table.
"""

from __future__ import annotations

from dataclasses import dataclass

from seed.seed_animals_distribution import SEEDED_CAT_BREEDS, SEEDED_DOG_BREEDS

_ENERGY_RANK = {"low": 0, "medium": 1, "high": 2}


@dataclass(frozen=True)
class BreedTraits:
    energy_level: str        # "low" | "medium" | "high"
    grooming_needs: str      # "low" | "medium" | "high"
    shedding_level: str      # "low" | "medium" | "high"
    hypoallergenic: bool
    apartment_friendly: bool
    kid_friendly: bool
    beginner_friendly: bool


def _traits(energy, grooming, shedding, hypoallergenic, apartment, kid, beginner) -> BreedTraits:
    return BreedTraits(
        energy_level=energy,
        grooming_needs=grooming,
        shedding_level=shedding,
        hypoallergenic=hypoallergenic,
        apartment_friendly=apartment,
        kid_friendly=kid,
        beginner_friendly=beginner,
    )


# breed -> (energy, grooming, shedding, hypoallergenic, apartment_friendly, kid_friendly, beginner_friendly)
_DOG_TRAIT_ROWS: dict[str, tuple] = {
    # Companion & Toy
    "Affenpinscher": ("medium", "medium", "low", False, True, False, False),
    "Biewer Terrier": ("medium", "high", "low", False, True, True, True),
    "Bolognese": ("low", "high", "low", True, True, True, True),
    "Brussels Griffon": ("medium", "medium", "low", False, True, False, False),
    "Cavalier King Charles Spaniel": ("medium", "medium", "medium", False, True, True, True),
    "Chihuahua": ("medium", "low", "low", False, True, False, True),
    "Chinese Crested": ("medium", "medium", "low", True, True, False, False),
    "English Toy Spaniel": ("low", "medium", "medium", False, True, True, True),
    "French Bulldog": ("low", "low", "medium", False, True, True, True),
    "Havanese": ("medium", "high", "low", True, True, True, True),
    "Italian Greyhound": ("medium", "low", "low", False, True, False, False),
    "Japanese Chin": ("low", "medium", "medium", False, True, True, True),
    "Maltese": ("low", "high", "low", True, True, True, True),
    "Miniature Pinscher": ("high", "low", "low", False, True, False, False),
    "Papillon": ("medium", "medium", "medium", False, True, True, True),
    "Pekingese": ("low", "high", "medium", False, True, False, False),
    "Pomeranian": ("medium", "high", "high", False, True, False, True),
    "Pug": ("low", "low", "high", False, True, True, True),
    "Russian Tsvetnaya Bolonka": ("medium", "medium", "low", True, True, True, True),
    "Shih Tzu": ("low", "high", "low", True, True, True, True),
    "Toy Poodle": ("medium", "high", "low", True, True, True, True),
    "Yorkshire Terrier": ("medium", "high", "low", True, True, False, True),
    # Sporting & Hound
    "Afghan Hound": ("high", "high", "medium", False, False, False, False),
    "American Water Spaniel": ("high", "medium", "medium", False, False, True, True),
    "Basenji": ("high", "low", "low", False, True, True, False),
    "Basset Fauve de Bretagne": ("medium", "low", "medium", False, True, True, True),
    "Basset Hound": ("low", "low", "high", False, True, True, True),
    "Beagle": ("high", "low", "medium", False, True, True, True),
    "Black and Tan Coonhound": ("medium", "low", "medium", False, False, True, True),
    "Bloodhound": ("medium", "low", "medium", False, False, True, False),
    "Borzoi": ("medium", "medium", "medium", False, False, False, False),
    "Boykin Spaniel": ("high", "medium", "medium", False, False, True, True),
    "Brittany": ("high", "medium", "medium", False, False, True, True),
    "Chesapeake Bay Retriever": ("high", "medium", "high", False, False, True, False),
    "Cocker Spaniel": ("medium", "high", "medium", False, True, True, True),
    "Dachshund": ("medium", "low", "medium", False, True, False, True),
    "English Cocker Spaniel": ("high", "high", "medium", False, True, True, True),
    "English Setter": ("high", "medium", "medium", False, False, True, True),
    "English Springer Spaniel": ("high", "medium", "medium", False, False, True, True),
    "German Shorthaired Pointer": ("high", "low", "medium", False, False, True, False),
    "Golden Retriever": ("high", "medium", "high", False, False, True, True),
    "Greyhound": ("medium", "low", "low", False, True, True, True),
    "Harrier": ("high", "low", "medium", False, False, True, True),
    "Irish Setter": ("high", "high", "medium", False, False, True, True),
    "Irish Wolfhound": ("medium", "medium", "medium", False, False, True, False),
    "Labrador Retriever": ("high", "low", "high", False, False, True, True),
    "Nova Scotia Duck Tolling Retriever": ("high", "medium", "medium", False, False, True, True),
    "Plott Hound": ("high", "low", "medium", False, False, True, False),
    "Pointer": ("high", "low", "medium", False, False, True, False),
    "Rhodesian Ridgeback": ("high", "low", "medium", False, False, True, False),
    "Saluki": ("high", "medium", "low", False, False, False, False),
    "Vizsla": ("high", "low", "medium", False, False, True, False),
    "Weimaraner": ("high", "low", "medium", False, False, True, False),
    "Whippet": ("medium", "low", "low", False, True, True, True),
    # Working & Herding
    "Akita": ("medium", "medium", "high", False, False, False, False),
    "Alaskan Malamute": ("high", "medium", "high", False, False, True, False),
    "Anatolian Shepherd Dog": ("medium", "low", "medium", False, False, True, False),
    "Australian Cattle Dog": ("high", "low", "medium", False, False, False, False),
    "Australian Shepherd": ("high", "medium", "high", False, False, True, False),
    "Bearded Collie": ("high", "high", "medium", False, False, True, True),
    "Belgian Malinois": ("high", "low", "high", False, False, False, False),
    "Belgian Sheepdog": ("high", "medium", "high", False, False, True, False),
    "Bernese Mountain Dog": ("medium", "medium", "high", False, False, True, True),
    "Black Russian Terrier": ("medium", "high", "low", False, False, False, False),
    "Boerboel": ("medium", "low", "medium", False, False, False, False),
    "Border Collie": ("high", "medium", "high", False, False, True, False),
    "Bouvier des Flandres": ("medium", "high", "low", False, False, True, False),
    "Boxer": ("high", "low", "medium", False, False, True, True),
    "Bullmastiff": ("low", "low", "medium", False, False, True, False),
    "Cardigan Welsh Corgi": ("medium", "medium", "high", False, True, True, True),
    "Cane Corso": ("medium", "low", "medium", False, False, False, False),
    "Collie": ("medium", "high", "high", False, False, True, True),
    "Doberman Pinscher": ("high", "low", "medium", False, False, True, False),
    "Dogue de Bordeaux": ("low", "low", "medium", False, False, True, False),
    "German Shepherd Dog": ("high", "medium", "high", False, False, True, False),
    "Great Dane": ("medium", "low", "medium", False, False, True, True),
    "Great Pyrenees": ("low", "high", "high", False, False, True, False),
    "Greater Swiss Mountain Dog": ("medium", "medium", "high", False, False, True, True),
    "Komondor": ("low", "high", "low", False, False, True, False),
    "Kuvasz": ("medium", "medium", "high", False, False, True, False),
    "Mastiff": ("low", "low", "medium", False, False, True, False),
    "Newfoundland": ("low", "high", "high", False, False, True, True),
    "Pembroke Welsh Corgi": ("medium", "medium", "high", False, True, True, True),
    "Portuguese Water Dog": ("high", "high", "low", True, False, True, True),
    "Rottweiler": ("medium", "low", "medium", False, False, False, False),
    "Saint Bernard": ("low", "medium", "high", False, False, True, True),
    "Samoyed": ("high", "high", "high", False, False, True, True),
    "Siberian Husky": ("high", "medium", "high", False, False, True, False),
    "Standard Schnauzer": ("high", "high", "low", True, False, True, True),
    # Terrier & Non-Sporting
    "Airedale Terrier": ("high", "high", "low", False, False, True, False),
    "American Hairless Terrier": ("high", "low", "low", True, True, True, True),
    "American Staffordshire Terrier": ("medium", "low", "medium", False, True, True, False),
    "Bedlington Terrier": ("medium", "high", "low", True, True, True, True),
    "Bichon Frise": ("medium", "high", "low", True, True, True, True),
    "Boston Terrier": ("medium", "low", "low", False, True, True, True),
    "Bull Terrier": ("high", "low", "medium", False, True, False, False),
    "Cairn Terrier": ("medium", "medium", "low", False, True, True, True),
    "Chow Chow": ("low", "high", "high", False, True, False, False),
    "Dalmatian": ("high", "low", "high", False, False, True, False),
    "Finnish Spitz": ("high", "medium", "high", False, False, True, True),
    "Irish Terrier": ("high", "medium", "low", False, False, True, False),
    "Keeshond": ("medium", "high", "high", False, True, True, True),
    "Lhasa Apso": ("low", "high", "low", True, True, False, False),
    "Miniature Schnauzer": ("medium", "high", "low", True, True, True, True),
    "Norwich Terrier": ("high", "medium", "low", False, True, True, True),
    "Poodle": ("high", "high", "low", True, True, True, True),
    "Rat Terrier": ("high", "low", "low", False, True, True, True),
    "Russell Terrier": ("high", "low", "medium", False, False, False, False),
    "Schipperke": ("high", "medium", "medium", False, True, True, False),
    "Scottish Terrier": ("medium", "high", "low", False, True, False, False),
    "Shar-Pei": ("low", "low", "low", False, True, False, False),
    "Shiba Inu": ("medium", "medium", "high", False, True, False, False),
    "Soft Coated Wheaten Terrier": ("high", "high", "low", True, True, True, True),
    "Staffordshire Bull Terrier": ("high", "low", "medium", False, True, True, True),
    "Teddy Roosevelt Terrier": ("high", "low", "low", False, True, True, True),
    "Tibetan Terrier": ("medium", "high", "low", True, True, True, True),
    "West Highland White Terrier": ("medium", "medium", "low", False, True, True, True),
}

# breed -> (energy, grooming, shedding, hypoallergenic, apartment_friendly, kid_friendly, beginner_friendly)
_CAT_TRAIT_ROWS: dict[str, tuple] = {
    # Shorthair & Traditional
    "Abyssinian": ("high", "low", "low", False, True, True, True),
    "American Shorthair": ("medium", "low", "medium", False, True, True, True),
    "American Wirehair": ("medium", "low", "medium", False, True, True, True),
    "Australian Mist": ("medium", "low", "medium", False, True, True, True),
    "Bombay": ("medium", "low", "low", False, True, True, True),
    "British Shorthair": ("low", "low", "medium", False, True, True, True),
    "Burmese": ("medium", "low", "low", False, True, True, True),
    "Burmilla": ("medium", "low", "low", False, True, True, True),
    "Chartreux": ("low", "low", "medium", False, True, True, True),
    "Colorpoint Shorthair": ("high", "low", "low", False, True, True, True),
    "Egyptian Mau": ("high", "low", "low", False, True, False, True),
    "European Burmese": ("medium", "low", "low", False, True, True, True),
    "Exotic Shorthair": ("low", "medium", "medium", False, True, True, True),
    "Havana Brown": ("medium", "low", "low", False, True, True, True),
    "Korat": ("medium", "low", "low", False, True, True, True),
    "Ocicat": ("high", "low", "low", False, True, True, True),
    "Oriental Shorthair": ("high", "low", "low", False, True, True, True),
    "Russian Blue": ("medium", "low", "low", True, True, True, True),
    "Siamese": ("high", "low", "low", False, True, True, True),
    "Singapura": ("high", "low", "low", False, True, True, True),
    "Snowshoe": ("medium", "low", "low", False, True, True, True),
    "Thai": ("high", "low", "low", False, True, True, True),
    "Tonkinese": ("high", "low", "low", False, True, True, True),
    # Longhair & Fluffy
    "Balinese": ("medium", "medium", "low", True, True, True, True),
    "Birman": ("low", "medium", "medium", False, True, True, True),
    "British Longhair": ("low", "medium", "medium", False, True, True, True),
    "Himalayan": ("low", "high", "high", False, True, True, False),
    "Javanese": ("high", "medium", "low", False, True, True, True),
    "Maine Coon": ("medium", "medium", "high", False, True, True, True),
    "Norwegian Forest Cat": ("medium", "medium", "high", False, True, True, True),
    "Persian": ("low", "high", "high", False, True, True, False),
    "Ragamuffin": ("low", "medium", "medium", False, True, True, True),
    "Ragdoll": ("low", "medium", "medium", False, True, True, True),
    "Scottish Fold Longhair": ("low", "medium", "medium", False, True, True, True),
    "Siberian": ("medium", "medium", "high", True, True, True, True),
    "Somali": ("high", "medium", "medium", False, True, True, True),
    "Turkish Angora": ("high", "medium", "medium", False, True, True, True),
    "Turkish Van": ("high", "medium", "medium", False, True, True, True),
    # Unique Mutations
    "American Bobtail": ("medium", "medium", "medium", False, True, True, True),
    "American Curl": ("medium", "low", "low", False, True, True, True),
    "Bambino": ("medium", "low", "low", True, True, True, False),
    "Bengal": ("high", "low", "low", False, False, True, False),
    "Chausie": ("high", "low", "low", False, False, False, False),
    "Cornish Rex": ("high", "low", "low", True, True, True, True),
    "Cymric": ("medium", "medium", "medium", False, True, True, True),
    "Devon Rex": ("high", "low", "low", True, True, True, True),
    "Donskoy": ("medium", "low", "low", True, True, True, False),
    "Highlander": ("high", "low", "medium", False, True, True, True),
    "Japanese Bobtail": ("high", "low", "low", False, True, True, True),
    "Kurilian Bobtail": ("medium", "medium", "medium", False, True, True, True),
    "LaPerm": ("medium", "medium", "low", True, True, True, True),
    "Lykoi": ("medium", "low", "low", False, True, False, False),
    "Manx": ("medium", "medium", "medium", False, True, True, True),
    "Munchkin": ("medium", "low", "medium", False, True, True, True),
    "Peterbald": ("medium", "low", "low", True, True, True, False),
    "Pixiebob": ("medium", "low", "medium", False, True, True, True),
    "Savannah": ("high", "low", "low", False, False, False, False),
    "Scottish Fold": ("low", "medium", "medium", False, True, True, True),
    "Selkirk Rex": ("low", "medium", "medium", False, True, True, True),
    "Sphynx": ("high", "medium", "low", True, True, True, False),
    "Toyger": ("high", "low", "low", False, True, True, True),
}

DOG_BREED_TRAITS: dict[str, BreedTraits] = {breed: _traits(*row) for breed, row in _DOG_TRAIT_ROWS.items()}
CAT_BREED_TRAITS: dict[str, BreedTraits] = {breed: _traits(*row) for breed, row in _CAT_TRAIT_ROWS.items()}

EXERCISE_NEEDS_TEXT = {
    "low": "Minimal — short walks or play sessions are plenty.",
    "medium": "Moderate — daily walks and regular playtime.",
    "high": "High — vigorous daily exercise or a job/task to do.",
}


def breed_traits(species: str, breed: str | None) -> BreedTraits | None:
    """Look up structured lifestyle traits for a breed, or None if unknown."""
    if not breed:
        return None
    table = DOG_BREED_TRAITS if species == "dog" else CAT_BREED_TRAITS
    return table.get(breed)


def exercise_needs_text(traits: BreedTraits) -> str:
    """Human-readable exercise guidance derived from energy_level."""
    return EXERCISE_NEEDS_TEXT[traits.energy_level]


assert set(DOG_BREED_TRAITS) == set(SEEDED_DOG_BREEDS), "DOG_BREED_TRAITS must cover every seeded dog breed"
assert set(CAT_BREED_TRAITS) == set(SEEDED_CAT_BREEDS), "CAT_BREED_TRAITS must cover every seeded cat breed"
