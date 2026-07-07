"""Master seeder for the PawPal+ clinic.

Builds the full dog-and-cat clinic roster in one pass. Each run rebuilds
data.json from scratch.

Medical data (breed chronic conditions and genetic-risk markers) was verified
against veterinary references — VCA Animal Hospitals, the Merck Veterinary
Manual, PetMD, and breed health surveys — rather than generated freehand. Key
corrections captured: Siberian Huskies are low-risk for hip dysplasia (their
real hereditary risks are eye conditions); Scottish Folds always carry
osteochondrodysplasia (it's the fold gene itself). Senior-onset conditions
(e.g., feline kidney disease) are age-gated.
"""

import random
import sys

from pawpal_system import Owner, Pet, save_owners_to_json
from seed.seed_dog_and_cat import DOG_AND_CAT_SPECIES

DATA_PATH = "data.json"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OWNER_NAMES = [
    "James Smith", "Mary Johnson", "Robert Williams", "Patricia Brown", "John Jones",
    "Jennifer Garcia", "Michael Miller", "Linda Davis", "David Rodriguez", "Elizabeth Martinez",
    "William Hernandez", "Barbara Lopez", "Richard Gonzalez", "Susan Wilson", "Joseph Anderson",
    "Jessica Thomas", "Thomas Taylor", "Sarah Moore", "Christopher Jackson", "Karen Martin",
    "Charles Lee", "Lisa Perez", "Daniel Thompson", "Nancy White", "Matthew Harris",
    "Betty Sanchez", "Anthony Clark", "Sandra Ramirez", "Mark Lewis", "Margaret Robinson",
    "Donald Walker", "Ashley Young", "Steven Allen", "Kimberly King", "Andrew Wright",
    "Emily Scott", "Paul Torres", "Donna Nguyen", "Joshua Hill", "Michelle Flores",
    "Kenneth Green", "Carol Adams", "Kevin Nelson", "Amanda Baker", "Brian Hall",
    "Melissa Rivera", "George Campbell", "Deborah Mitchell", "Edward Carter", "Stephanie Roberts",
    "Alan Turing", "Marie Curie", "Nikola Tesla", "Ada Lovelace", "Grace Hopper",
    "Albert Einstein", "Isaac Newton", "Galileo Galilei", "Charles Darwin", "Stephen Hawking",
    "Rosalind Franklin", "Jane Goodall", "Carl Sagan", "Neil deGrasse Tyson", "Bill Nye",
    "Steve Irwin", "David Attenborough", "Jacques Cousteau", "Sylvia Earle", "Rachel Carson",
    "Walt Disney", "Jim Henson", "Stan Lee", "Jack Kirby", "Hayao Miyazaki",
    "Arthur Conan Doyle", "Agatha Christie", "Stephen King", "J.K. Rowling", "J.R.R. Tolkien",
    "Liam Gallagher", "Emma Thompson", "Noah Williams", "Olivia Brown", "Aria Parker",
    "Elijah Walker", "Charlotte Hall", "Lucas Allen", "Amelia Young", "Mason King",
    "Harper Wright", "Logan Scott", "Evelyn Torres", "Alexander Nguyen", "Abigail Hill",
    "Ethan Flores", "Emily Green", "Jacob Adams", "Elizabeth Nelson", "Michael Baker",
    "William Jones", "Ava Garcia", "James Martinez", "Isabella Robinson", "Oliver Clark",
    "Sophia Rodriguez", "Benjamin Lewis", "Mia Lee", "Mila Rivera", "Daniel Campbell",
    "Ella Mitchell", "Henry Carter", "Avery Roberts", "Jackson Gomez", "Sofia Phillips",
    "Sebastian Evans", "Camila Turner", "Aiden Diaz", "Matthew Cruz", "Scarlett Edwards",
    "Samuel Collins", "Victoria Reyes", "David Stewart", "Madison Morris", "Joseph Morales",
    "Luna Murphy", "Carter Cook", "Grace Rogers", "Owen Gutierrez", "Chloe Ortiz",
    "Wyatt Morgan", "Penelope Cooper", "John Peterson", "Layla Bailey", "Luke Reed",
    "Zoe Jenkins", "Levi Ward", "Stella Brooks", "Gabriel Kelly", "Nora Sanders",
    "Florence Nightingale", "Clara Barton", "Mary Seacole", "Elizabeth Blackwell", "Dorothea Dix",
    "Virginia Apgar", "Jonas Salk", "Alexander Fleming", "Louis Pasteur", "Edward Jenner",
    "George Lucas", "Steven Spielberg", "Martin Scorsese", "Alfred Hitchcock", "Stanley Kubrick",
    "Quentin Tarantino", "Christopher Nolan", "James Cameron", "Peter Jackson", "Ridley Scott",
    "John Williams", "Hans Zimmer", "Ennio Morricone", "Danny Elfman", "Howard Shore",
    "George R.R. Martin", "Isaac Asimov", "Arthur C. Clarke", "Philip K. Dick", "Frank Herbert",
]

PET_NAMES = [
    "Bella", "Luna", "Charlie", "Lucy", "Cooper",
    "Max", "Bailey", "Daisy", "Sadie", "Maggie",
    "Rocky", "Oreo", "Buster", "Chloe", "Sophie",
    "Lily", "Stella", "Molly", "Penny", "Lola",
    "Shelly", "Speedy", "Ninja", "Bubbles", "Flipper",
    "Spike", "Pip", "Squeak", "Apollo", "Sunny",
    "Nibbles", "Shadow", "Pippin", "Gizmo", "Yoshi",
    "Draco", "Finn", "Nemo", "Dory", "Mochi",
    "Peanut", "Barnaby", "Thor", "Cleo", "Jasper",
    "Ruby", "Simba", "Coco", "Bandit", "Hazel",
    "Blue", "Pepper", "Oscar", "Dexter", "Toby",
    "Winston", "Olive", "Milo", "Leo", "Loki",
    "Chester", "Felix", "Pumpkin", "Rosie", "Archie",
    "Willow", "Roxy", "Zeus", "Winnie", "Gus",
    "Duke", "Bear", "Tucker", "Murphy", "Oliver",
    "Harley", "Riley", "Marley", "Scout", "Jax",
    "Koda", "Mac", "Diesel", "Louie", "Hank",
    "Boomer", "Bruce", "Frankie", "Ghost", "Gunner",
    "Hunter", "Jack", "Kobe", "Moose", "Rex",
    "Rocco", "Sam", "Ziggy", "Mango", "Kiwi",
]

SPECIES = DOG_AND_CAT_SPECIES

# Breed -> realistic weight range in lbs (upper bounds allow a chunky pet).
# Dogs and cats get their weight rolled from their breed's range, so a
# Chihuahua never outweighs a Great Dane.
DOG_BREEDS = {
    "Labrador Retriever": (55, 90), "German Shepherd": (50, 95), "Golden Retriever": (55, 80),
    "French Bulldog": (16, 30), "Bulldog": (40, 55), "Poodle": (40, 70),
    "Beagle": (18, 35), "Rottweiler": (80, 135), "Dachshund": (11, 32),
    "Yorkshire Terrier": (4, 10), "Chihuahua": (3, 9), "Great Dane": (110, 175),
    "Shih Tzu": (9, 18), "Siberian Husky": (35, 60), "Boxer": (55, 80),
    "Pembroke Welsh Corgi": (22, 33), "Border Collie": (30, 55), "Australian Shepherd": (40, 65),
    "Pit Bull Terrier": (30, 65), "Mixed Breed": (15, 90),
}
CAT_BREEDS = {
    "Domestic Shorthair": (8, 18), "Domestic Longhair": (8, 18), "Maine Coon": (10, 25),
    "Siamese": (6, 14), "Persian": (7, 15), "Ragdoll": (10, 20),
    "Bengal": (8, 16), "Sphynx": (6, 14), "British Shorthair": (7, 17),
    "Russian Blue": (7, 15), "Scottish Fold": (6, 13), "Norwegian Forest Cat": (9, 20),
}

# Common real-world dog/cat allergies (food and environmental).
DOG_CAT_ALLERGIES = [
    "Chicken", "Beef", "Dairy", "Wheat / Grain", "Egg", "Lamb", "Soy",
    "Flea Saliva", "Pollen", "Dust Mites", "Grass", "Mold Spores",
]

# ---------------------------------------------------------------------------
# Medical data (verified against veterinary sources — see module docstring).
#
# Two ideas are kept distinct:
#   * chronic       - conditions a pet can actually be *diagnosed* with.
#   * risk (marker) - a predisposition the pet does NOT have (hereditary,
#     breed-linked).
# ---------------------------------------------------------------------------

CONDITION_NOTES = [
    "diagnosed, managed with medication", "mild, diet-controlled",
    "stable, monitored at checkups", "flares up seasonally", "requires ongoing treatment",
]

# Conditions that should only appear in older animals (min age in years), so a
# 1-year-old cat never rolls kidney disease.
CONDITION_MIN_AGE = {
    "Chronic Kidney Disease": 8, "Hyperthyroidism": 8, "Osteoarthritis": 7,
    "Arthritis": 7, "Diabetes": 6,
}

DOG_CHRONIC = ["Osteoarthritis", "Allergic Dermatitis (Atopy)", "Diabetes Mellitus",
               "Hypothyroidism", "Chronic Otitis (Ear Infections)"]
CAT_CHRONIC = ["Chronic Kidney Disease", "Hyperthyroidism", "Diabetes Mellitus",
               "Feline Asthma", "Dental Disease", "Inflammatory Bowel Disease"]

# Breed -> inherited conditions the breed is predisposed to (used as "at risk,
# not present" markers). Empty list = mixed ancestry -> "none identified".
DOG_BREED_RISKS = {
    "Labrador Retriever": ["Hip Dysplasia", "Progressive Retinal Atrophy"],
    "German Shepherd": ["Hip Dysplasia", "Degenerative Myelopathy"],
    "Golden Retriever": ["Hip Dysplasia", "Subvalvular Aortic Stenosis"],
    "French Bulldog": ["Brachycephalic Airway Syndrome", "Intervertebral Disc Disease"],
    "Bulldog": ["Brachycephalic Airway Syndrome", "Skin Fold Dermatitis"],
    "Poodle": ["Addison's Disease", "Progressive Retinal Atrophy"],
    "Beagle": ["Epilepsy", "Hypothyroidism"],
    "Rottweiler": ["Osteosarcoma", "Hip Dysplasia"],
    "Dachshund": ["Intervertebral Disc Disease", "Luxating Patella"],
    "Yorkshire Terrier": ["Tracheal Collapse", "Luxating Patella"],
    "Chihuahua": ["Luxating Patella", "Mitral Valve Disease"],
    "Great Dane": ["Bloat (GDV)", "Dilated Cardiomyopathy"],
    "Shih Tzu": ["Brachycephalic Airway Syndrome", "Dry Eye (KCS)"],
    # Huskies are one of the LOWEST hip-dysplasia breeds; their real hereditary
    # risks are eye conditions (cataracts ~8%, corneal dystrophy ~3%).
    "Siberian Husky": ["Hereditary Cataracts", "Corneal Dystrophy"],
    "Boxer": ["Boxer Cardiomyopathy (ARVC)", "Mast Cell Tumors"],
    "Pembroke Welsh Corgi": ["Degenerative Myelopathy", "Intervertebral Disc Disease"],
    "Border Collie": ["Collie Eye Anomaly", "Epilepsy"],
    "Australian Shepherd": ["MDR1 Drug Sensitivity", "Collie Eye Anomaly"],
    "Pit Bull Terrier": ["Hip Dysplasia", "Demodectic Mange"],
    "Mixed Breed": [],
}
CAT_BREED_RISKS = {
    "Domestic Shorthair": [], "Domestic Longhair": [],
    "Maine Coon": ["Hypertrophic Cardiomyopathy", "Hip Dysplasia"],
    "Siamese": ["Progressive Retinal Atrophy", "Feline Asthma"],
    "Persian": ["Polycystic Kidney Disease", "Brachycephalic Airway Syndrome"],
    "Ragdoll": ["Hypertrophic Cardiomyopathy"],
    "Bengal": ["Progressive Retinal Atrophy", "Hypertrophic Cardiomyopathy"],
    "Sphynx": ["Hypertrophic Cardiomyopathy", "Hereditary Myopathy"],
    "British Shorthair": ["Hypertrophic Cardiomyopathy", "Polycystic Kidney Disease"],
    "Russian Blue": ["Obesity (breed tendency)"],
    # Osteochondrodysplasia is caused by the fold gene, so every fold-eared cat
    # HAS it (handled as an always-present condition below). Their at-risk
    # markers are the cardiac/kidney conditions instead.
    "Scottish Fold": ["Hypertrophic Cardiomyopathy", "Polycystic Kidney Disease"],
    "Norwegian Forest Cat": ["Glycogen Storage Disease IV", "Hypertrophic Cardiomyopathy"],
}
# Breeds where the defining trait IS a lifelong condition, so every one has it.
BREED_ALWAYS_HAS = {
    "Scottish Fold": "Osteochondrodysplasia: inherited cartilage & joint disease — present in all fold-eared cats",
}

# Behavior notes a vet clinic might keep on file.
DOG_BEHAVIOR_NOTES = [
    "Friendly with strangers", "Pulls hard on leash", "Anxious during thunderstorms",
    "Food-motivated, easy to train", "Barks at delivery drivers",
    "Gets along well with other dogs", "Nervous at the vet — approach slowly",
    "High energy, needs daily walks", "Separation anxiety when left alone",
    "Protective of food bowl", "Excellent recall off-leash",
    "Scared of vacuum cleaners", "Jumps on guests when excited",
    "Calm and gentle with children", "Loves belly rubs",
]
CAT_BEHAVIOR_NOTES = [
    "Shy — hides from strangers", "Very vocal, especially at mealtimes",
    "Does not tolerate nail trims", "Loves lap time", "Midnight zoomies",
    "Swats when overstimulated", "Indoor only — known door-dasher",
    "Gets along with other cats", "Hisses at the carrier",
    "Enjoys being brushed", "Knocks things off tables",
    "Friendly with dogs", "Needs slow introductions to new people",
    "Territorial around the litter box",
]


def random_allergies():
    """Return 1-2 random allergies for a dog/cat, or 'No Allergies' about half the time."""
    if random.random() < 0.5:
        return "No Allergies"
    return ", ".join(random.sample(DOG_CAT_ALLERGIES, random.randint(1, 2)))


def random_behavior_notes(species):
    """Return 1-2 species-appropriate behavior notes for a dog or cat."""
    notes = DOG_BEHAVIOR_NOTES if species == "dog" else CAT_BEHAVIOR_NOTES
    return "; ".join(random.sample(notes, random.randint(1, 2)))


def plural(breed):
    """Pluralize a breed name ('Husky' -> 'Huskies', 'Poodle' -> 'Poodles')."""
    if breed.endswith("y") and breed[-2].lower() not in "aeiou":
        return breed[:-1] + "ies"
    if breed.endswith(("s", "sh", "ch", "x")):
        return breed + "es"
    return breed + "s"


def _condition_min_age(condition):
    """Youngest age (years) at which a condition realistically appears; 0 if any age."""
    for key, min_age in CONDITION_MIN_AGE.items():
        if key.lower() in condition.lower():
            return min_age
    return 0


def _format_marker(condition, subject):
    """Phrase a hereditary at-risk marker for a breed."""
    return f"Hereditary risk — {condition}: hereditary in {subject} — not present, monitor at checkups"


def random_medical_history(species, breed, age=1, sex=None):
    """Build a chronic_conditions list: an age-appropriate diagnosis (~45%) plus a risk marker."""
    chronic_pool = DOG_CHRONIC if species == "dog" else CAT_CHRONIC
    risk_table = DOG_BREED_RISKS if species == "dog" else CAT_BREED_RISKS
    risks = risk_table[breed]
    subject = plural(breed)

    entries = []

    # Breeds whose defining trait is itself a condition always carry it.
    if breed in BREED_ALWAYS_HAS:
        entries.append(BREED_ALWAYS_HAS[breed])

    # ~45% of pets carry an actual diagnosis, filtered to be age-appropriate.
    if random.random() < 0.45:
        eligible = [c for c in chronic_pool if age >= _condition_min_age(c)]
        for condition in random.sample(eligible, min(len(eligible), random.randint(1, 2))):
            entries.append(f"{condition}: {random.choice(CONDITION_NOTES)}")

    # One risk marker: a hereditary predisposition the pet does NOT currently have.
    open_risks = [c for c in risks if not any(e.startswith(c) for e in entries)]
    if open_risks:
        entries.append(_format_marker(random.choice(open_risks), subject))
    elif not risks:
        entries.append("Hereditary risk: none identified (mixed ancestry)")

    return entries


def generate_random_pet(pet_name, species_tuple):
    """Build a Pet with standard stats for a dog or cat."""
    species, _category = species_tuple
    breeds = DOG_BREEDS if species == "dog" else CAT_BREEDS
    breed = random.choice(list(breeds))
    low, high = breeds[breed]
    age, sex = random.randint(1, 15), random.choice(["Male", "Female"])
    return Pet(
        name=pet_name, species=species, breed=breed, age=age, sex=sex,
        weight=f"{random.randint(low, high)} lbs", height=f"{random.randint(10, 30)} inches",
        allergies=random_allergies(), behavioral_notes=random_behavior_notes(species),
        chronic_conditions=random_medical_history(species, breed, age, sex),
        color_markings=random.choice(["Black", "White", "Brown", "Spotted", "Golden", "Tabby", "Calico"]),
        spayed_neutered=random.choice(["Yes", "No"]), microchip_number=f"9810{random.randint(100000000, 999999999)}",
        diet_good=["Dry Kibble", "Wet Food", "Carrots"], diet_bad=["Chocolate", "Grapes", "Onions", "Garlic"]
    )


def build_distribution(total):
    """Plan one species per owner: roughly half dogs, half cats."""
    distribution = list(SPECIES)  # guarantees both dog and cat appear at least once

    extra = total - len(distribution)
    extra_dogs = extra // 2
    extra_cats = extra - extra_dogs
    distribution += [("dog", "mammal")] * extra_dogs + [("cat", "mammal")] * extra_cats

    random.shuffle(distribution)
    return distribution


def seed_animals_list():
    """Rebuild data.json from scratch with the full dog-and-cat clinic roster."""
    distribution = build_distribution(len(OWNER_NAMES))

    owners = []
    for i, owner_name in enumerate(OWNER_NAMES):
        owner = Owner(owner_name)
        pet = generate_random_pet(PET_NAMES[i % len(PET_NAMES)], distribution[i])
        owner.add_pet(pet)
        owners.append(owner)

    save_owners_to_json(owners, DATA_PATH)

    dogs = sum(1 for d in distribution if d[0] == "dog")
    cats = sum(1 for d in distribution if d[0] == "cat")
    print(f"🏥 CLINIC BUILT! {len(owners)} owners: {dogs} dogs, {cats} cats.")


seed_master_list = seed_animals_list


if __name__ == "__main__":
    seed_animals_list()
