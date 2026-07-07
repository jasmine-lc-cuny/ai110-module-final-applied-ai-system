"""Master seeder for the PawPal+ clinic.

Builds one patient per breed from a comprehensive dog- and cat-breed list
(117 dog breeds across Companion & Toy, Sporting & Hound, Working & Herding,
and Terrier & Non-Sporting groups; 61 cat breeds across Shorthair &
Traditional, Longhair & Fluffy, and Unique Mutations groups) — every breed
appears exactly once, each with a unique owner name and a unique pet name.
Each run rebuilds data.json from scratch.

Medical data (breed chronic conditions and hereditary risk markers) reflects
well-documented breed tendencies where known (e.g. hip dysplasia in large
working breeds, HCM in Maine Coons/Ragdolls/British Shorthairs, the
osteochondrodysplasia every fold-eared cat carries). For breeds without a
well-established, specific inherited condition, the risk list is left empty
rather than inventing one — "Hereditary risk: none identified" is a
legitimate, honest answer, not a placeholder.
"""

import random
import sys

from pawpal_system import Owner, Pet, save_owners_to_json

DATA_PATH = "data.json"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Breed lists — one patient will be seeded per breed, in this order (shuffled
# only for owner/pet name pairing, not for breed selection).
# ---------------------------------------------------------------------------

DOG_BREEDS_COMPANION_TOY = [
    "Affenpinscher", "Biewer Terrier", "Bolognese", "Brussels Griffon",
    "Cavalier King Charles Spaniel", "Chihuahua", "Chinese Crested",
    "English Toy Spaniel", "French Bulldog", "Havanese", "Italian Greyhound",
    "Japanese Chin", "Maltese", "Miniature Pinscher", "Papillon", "Pekingese",
    "Pomeranian", "Pug", "Russian Tsvetnaya Bolonka", "Shih Tzu", "Toy Poodle",
    "Yorkshire Terrier",
]
DOG_BREEDS_SPORTING_HOUND = [
    "Afghan Hound", "American Water Spaniel", "Basenji",
    "Basset Fauve de Bretagne", "Basset Hound", "Beagle",
    "Black and Tan Coonhound", "Bloodhound", "Borzoi", "Boykin Spaniel",
    "Brittany", "Chesapeake Bay Retriever", "Cocker Spaniel", "Dachshund",
    "English Cocker Spaniel", "English Setter", "English Springer Spaniel",
    "German Shorthaired Pointer", "Golden Retriever", "Greyhound", "Harrier",
    "Irish Setter", "Irish Wolfhound", "Labrador Retriever",
    "Nova Scotia Duck Tolling Retriever", "Plott Hound", "Pointer",
    "Rhodesian Ridgeback", "Saluki", "Vizsla", "Weimaraner", "Whippet",
]
DOG_BREEDS_WORKING_HERDING = [
    "Akita", "Alaskan Malamute", "Anatolian Shepherd Dog",
    "Australian Cattle Dog", "Australian Shepherd", "Bearded Collie",
    "Belgian Malinois", "Belgian Sheepdog", "Bernese Mountain Dog",
    "Black Russian Terrier", "Boerboel", "Border Collie",
    "Bouvier des Flandres", "Boxer", "Bullmastiff", "Cardigan Welsh Corgi",
    "Cane Corso", "Collie", "Doberman Pinscher", "Dogue de Bordeaux",
    "German Shepherd Dog", "Great Dane", "Great Pyrenees",
    "Greater Swiss Mountain Dog", "Komondor", "Kuvasz", "Mastiff",
    "Newfoundland", "Pembroke Welsh Corgi", "Portuguese Water Dog",
    "Rottweiler", "Saint Bernard", "Samoyed", "Siberian Husky",
    "Standard Schnauzer",
]
DOG_BREEDS_TERRIER_NONSPORTING = [
    "Airedale Terrier", "American Hairless Terrier",
    "American Staffordshire Terrier", "Bedlington Terrier", "Bichon Frise",
    "Boston Terrier", "Bull Terrier", "Cairn Terrier", "Chow Chow",
    "Dalmatian", "Finnish Spitz", "Irish Terrier", "Keeshond", "Lhasa Apso",
    "Miniature Schnauzer", "Norwich Terrier", "Poodle", "Rat Terrier",
    "Russell Terrier", "Schipperke", "Scottish Terrier", "Shar-Pei",
    "Shiba Inu", "Soft Coated Wheaten Terrier", "Staffordshire Bull Terrier",
    "Teddy Roosevelt Terrier", "Tibetan Terrier", "West Highland White Terrier",
]

SEEDED_DOG_BREEDS = (
    DOG_BREEDS_COMPANION_TOY
    + DOG_BREEDS_SPORTING_HOUND
    + DOG_BREEDS_WORKING_HERDING
    + DOG_BREEDS_TERRIER_NONSPORTING
)

CAT_BREEDS_SHORTHAIR_TRADITIONAL = [
    "Abyssinian", "American Shorthair", "American Wirehair", "Australian Mist",
    "Bombay", "British Shorthair", "Burmese", "Burmilla", "Chartreux",
    "Colorpoint Shorthair", "Egyptian Mau", "European Burmese",
    "Exotic Shorthair", "Havana Brown", "Korat", "Ocicat", "Oriental Shorthair",
    "Russian Blue", "Siamese", "Singapura", "Snowshoe", "Thai", "Tonkinese",
]
CAT_BREEDS_LONGHAIR_FLUFFY = [
    "Balinese", "Birman", "British Longhair", "Himalayan", "Javanese",
    "Maine Coon", "Norwegian Forest Cat", "Persian", "Ragamuffin", "Ragdoll",
    "Scottish Fold Longhair", "Siberian", "Somali", "Turkish Angora",
    "Turkish Van",
]
CAT_BREEDS_UNIQUE_MUTATIONS = [
    "American Bobtail", "American Curl", "Bambino", "Bengal", "Chausie",
    "Cornish Rex", "Cymric", "Devon Rex", "Donskoy", "Highlander",
    "Japanese Bobtail", "Kurilian Bobtail", "LaPerm", "Lykoi", "Manx",
    "Munchkin", "Peterbald", "Pixiebob", "Savannah", "Scottish Fold",
    "Selkirk Rex", "Sphynx", "Toyger",
]

SEEDED_CAT_BREEDS = (
    CAT_BREEDS_SHORTHAIR_TRADITIONAL
    + CAT_BREEDS_LONGHAIR_FLUFFY
    + CAT_BREEDS_UNIQUE_MUTATIONS
)

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
    "Nina Blackwood", "Derek Sandoval", "Priya Chandra", "Oscar Delacroix", "Wanda Kim",
    "Felix Okoro", "Greta Lindholm", "Marcus Aurelius Cole", "Yara Petrov", "Django Vance",
    "Selma Ortiz", "Tobias Renner", "Junie Prescott", "Rafael Castellano", "Ingrid Solheim",
    "Cormac Fitzgerald", "Aiko Tanaka", "Baxter Winslow", "Delia Marchetti", "Ezra Whitfield",
    "Fiona Blackthorn", "Gideon Marsh", "Hazel Winters", "Ignatius Boone", "Josephine Delarosa",
    "Kenji Watanabe", "Lucinda Faraday", "Milo Abernathy", "Nadia Kowalski", "Otis Brennan",
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
    "Biscuit", "Waffles", "Pancake", "Noodle", "Pretzel",
    "Bagel", "Muffin", "Cupcake", "Brownie", "Cinnamon",
    "Nutmeg", "Ginger", "Clover", "Maple", "Acorn",
    "Pebbles", "Boulder", "Storm", "Blaze", "Ember",
    "Comet", "Rocket", "Nova", "Orbit", "Pixel",
    "Bolt", "Turbo", "Zippy", "Doodle", "Sprinkle",
    "Marble", "Domino", "Checkers", "Patches", "Freckles",
    "Speckles", "Dot", "Squiggle", "Wiggles", "Bounce",
    "Hopper", "Skipper", "Anchor", "Compass", "Pilot",
    "Captain", "Admiral", "Sailor", "Voyager", "Journey",
    "Quest", "Ranger", "Trapper", "Tracker", "Blazer",
    "Rustler", "Maverick", "Buckaroo", "Cowboy", "Sundance",
    "Outlaw", "Renegade", "Justice", "Liberty", "Patriot",
    "Eagle", "Falcon", "Hawk", "Raven", "Phoenix",
    "Griffin", "Talon", "Thunder", "Lightning", "Cyclone",
    "Tornado", "Blizzard", "Frost", "Crystal", "Diamond",
    "Pearl", "Opal", "Jade", "Amber", "Sapphire",
    "Emerald", "Topaz", "Onyx", "Ebony", "Ivory",
]

# Breed -> realistic weight range in lbs (upper bounds allow a chunky pet).
DOG_BREEDS = {
    "Affenpinscher": (7, 10), "Biewer Terrier": (4, 8), "Bolognese": (5, 9),
    "Brussels Griffon": (6, 12), "Cavalier King Charles Spaniel": (13, 18),
    "Chihuahua": (3, 9), "Chinese Crested": (5, 12), "English Toy Spaniel": (8, 14),
    "French Bulldog": (16, 30), "Havanese": (7, 13), "Italian Greyhound": (7, 14),
    "Japanese Chin": (7, 11), "Maltese": (4, 7), "Miniature Pinscher": (8, 11),
    "Papillon": (5, 10), "Pekingese": (7, 14), "Pomeranian": (3, 7),
    "Pug": (14, 18), "Russian Tsvetnaya Bolonka": (4, 11), "Shih Tzu": (9, 18),
    "Toy Poodle": (4, 6), "Yorkshire Terrier": (4, 10),
    "Afghan Hound": (50, 60), "American Water Spaniel": (25, 45), "Basenji": (20, 25),
    "Basset Fauve de Bretagne": (25, 35), "Basset Hound": (40, 65), "Beagle": (18, 35),
    "Black and Tan Coonhound": (40, 75), "Bloodhound": (80, 110), "Borzoi": (55, 105),
    "Boykin Spaniel": (25, 40), "Brittany": (30, 40), "Chesapeake Bay Retriever": (55, 80),
    "Cocker Spaniel": (20, 30), "Dachshund": (11, 32), "English Cocker Spaniel": (26, 34),
    "English Setter": (45, 80), "English Springer Spaniel": (40, 50),
    "German Shorthaired Pointer": (45, 70), "Golden Retriever": (55, 80), "Greyhound": (60, 88),
    "Harrier": (45, 60), "Irish Setter": (60, 70), "Irish Wolfhound": (105, 180),
    "Labrador Retriever": (55, 90), "Nova Scotia Duck Tolling Retriever": (35, 50),
    "Plott Hound": (40, 60), "Pointer": (45, 75), "Rhodesian Ridgeback": (70, 85),
    "Saluki": (35, 65), "Vizsla": (45, 65), "Weimaraner": (55, 90), "Whippet": (25, 40),
    "Akita": (70, 130), "Alaskan Malamute": (75, 85), "Anatolian Shepherd Dog": (80, 150),
    "Australian Cattle Dog": (30, 50), "Australian Shepherd": (40, 65),
    "Bearded Collie": (45, 55), "Belgian Malinois": (40, 80), "Belgian Sheepdog": (45, 75),
    "Bernese Mountain Dog": (70, 115), "Black Russian Terrier": (80, 140),
    "Boerboel": (150, 200), "Border Collie": (30, 55), "Bouvier des Flandres": (60, 90),
    "Boxer": (55, 80), "Bullmastiff": (100, 130), "Cardigan Welsh Corgi": (25, 38),
    "Cane Corso": (90, 120), "Collie": (50, 75), "Doberman Pinscher": (60, 100),
    "Dogue de Bordeaux": (99, 110), "German Shepherd Dog": (50, 95), "Great Dane": (110, 175),
    "Great Pyrenees": (85, 100), "Greater Swiss Mountain Dog": (85, 140),
    "Komondor": (80, 100), "Kuvasz": (70, 115), "Mastiff": (120, 230),
    "Newfoundland": (100, 150), "Pembroke Welsh Corgi": (22, 33),
    "Portuguese Water Dog": (35, 60), "Rottweiler": (80, 135), "Saint Bernard": (120, 180),
    "Samoyed": (35, 65), "Siberian Husky": (35, 60), "Standard Schnauzer": (30, 50),
    "Airedale Terrier": (40, 65), "American Hairless Terrier": (12, 16),
    "American Staffordshire Terrier": (40, 70), "Bedlington Terrier": (17, 23),
    "Bichon Frise": (12, 18), "Boston Terrier": (12, 25), "Bull Terrier": (50, 70),
    "Cairn Terrier": (13, 18), "Chow Chow": (45, 70), "Dalmatian": (45, 70),
    "Finnish Spitz": (20, 33), "Irish Terrier": (25, 27), "Keeshond": (35, 45),
    "Lhasa Apso": (12, 18), "Miniature Schnauzer": (11, 20), "Norwich Terrier": (11, 12),
    "Poodle": (40, 70), "Rat Terrier": (10, 25), "Russell Terrier": (9, 15),
    "Schipperke": (10, 16), "Scottish Terrier": (18, 22), "Shar-Pei": (45, 60),
    "Shiba Inu": (17, 23), "Soft Coated Wheaten Terrier": (30, 40),
    "Staffordshire Bull Terrier": (24, 38), "Teddy Roosevelt Terrier": (8, 25),
    "Tibetan Terrier": (18, 30), "West Highland White Terrier": (15, 20),
}
CAT_BREEDS = {
    "Abyssinian": (8, 12), "American Shorthair": (8, 15), "American Wirehair": (8, 15),
    "Australian Mist": (8, 13), "Bombay": (8, 15), "British Shorthair": (7, 17),
    "Burmese": (8, 12), "Burmilla": (7, 12), "Chartreux": (7, 16),
    "Colorpoint Shorthair": (6, 10), "Egyptian Mau": (7, 11), "European Burmese": (8, 12),
    "Exotic Shorthair": (7, 14), "Havana Brown": (8, 11), "Korat": (6, 10),
    "Ocicat": (8, 15), "Oriental Shorthair": (6, 10), "Russian Blue": (7, 15),
    "Siamese": (6, 14), "Singapura": (4, 8), "Snowshoe": (7, 12), "Thai": (8, 12),
    "Tonkinese": (6, 12),
    "Balinese": (6, 11), "Birman": (8, 12), "British Longhair": (9, 18),
    "Himalayan": (7, 12), "Javanese": (6, 10), "Maine Coon": (10, 25),
    "Norwegian Forest Cat": (9, 20), "Persian": (7, 15), "Ragamuffin": (10, 20),
    "Ragdoll": (10, 20), "Scottish Fold Longhair": (6, 13), "Siberian": (10, 20),
    "Somali": (6, 10), "Turkish Angora": (5, 10), "Turkish Van": (9, 20),
    "American Bobtail": (7, 16), "American Curl": (5, 10), "Bambino": (4, 9),
    "Bengal": (8, 16), "Chausie": (12, 25), "Cornish Rex": (6, 10), "Cymric": (8, 12),
    "Devon Rex": (6, 9), "Donskoy": (6, 12), "Highlander": (10, 20),
    "Japanese Bobtail": (6, 10), "Kurilian Bobtail": (8, 15), "LaPerm": (6, 10),
    "Lykoi": (5, 8), "Manx": (8, 12), "Munchkin": (5, 9), "Peterbald": (6, 10),
    "Pixiebob": (8, 17), "Savannah": (12, 25), "Scottish Fold": (6, 13),
    "Selkirk Rex": (7, 16), "Sphynx": (6, 14), "Toyger": (7, 15),
}

# Common real-world dog/cat allergies (food and environmental).
DOG_CAT_ALLERGIES = [
    "Chicken", "Beef", "Dairy", "Wheat / Grain", "Egg", "Lamb", "Soy",
    "Flea Saliva", "Pollen", "Dust Mites", "Grass", "Mold Spores",
]

# ---------------------------------------------------------------------------
# Medical data. Two ideas are kept distinct:
#   * chronic  - conditions a pet can actually be *diagnosed* with (shared
#     across all dogs / all cats — not breed-specific).
#   * risk     - a breed-linked hereditary predisposition the pet does NOT
#     have. An empty list means no well-established, breed-specific inherited
#     condition is claimed for that breed.
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

DOG_BREED_RISKS = {
    "Affenpinscher": ["Patellar Luxation", "Legg-Calve-Perthes Disease"],
    "Biewer Terrier": ["Patellar Luxation", "Dental Disease"],
    "Bolognese": ["Patellar Luxation", "Dental Disease"],
    "Brussels Griffon": ["Patellar Luxation", "Brachycephalic Airway Syndrome"],
    "Cavalier King Charles Spaniel": ["Mitral Valve Disease", "Syringomyelia"],
    "Chihuahua": ["Luxating Patella", "Mitral Valve Disease"],
    "Chinese Crested": ["Patellar Luxation", "Progressive Retinal Atrophy"],
    "English Toy Spaniel": ["Mitral Valve Disease", "Patellar Luxation"],
    "French Bulldog": ["Brachycephalic Airway Syndrome", "Intervertebral Disc Disease"],
    "Havanese": ["Patellar Luxation", "Legg-Calve-Perthes Disease"],
    "Italian Greyhound": ["Patellar Luxation", "Progressive Retinal Atrophy"],
    "Japanese Chin": ["Patellar Luxation", "Brachycephalic Airway Syndrome"],
    "Maltese": ["Patellar Luxation", "Portosystemic Shunt"],
    "Miniature Pinscher": ["Patellar Luxation", "Legg-Calve-Perthes Disease"],
    "Papillon": ["Patellar Luxation", "Progressive Retinal Atrophy"],
    "Pekingese": ["Brachycephalic Airway Syndrome", "Intervertebral Disc Disease"],
    "Pomeranian": ["Patellar Luxation", "Tracheal Collapse"],
    "Pug": ["Brachycephalic Airway Syndrome", "Hemivertebrae"],
    "Russian Tsvetnaya Bolonka": ["Patellar Luxation", "Dental Disease"],
    "Shih Tzu": ["Brachycephalic Airway Syndrome", "Dry Eye (KCS)"],
    "Toy Poodle": ["Patellar Luxation", "Progressive Retinal Atrophy"],
    "Yorkshire Terrier": ["Tracheal Collapse", "Luxating Patella"],
    "Afghan Hound": ["Hypothyroidism", "Cataracts"],
    "American Water Spaniel": ["Hip Dysplasia", "Chronic Otitis"],
    "Basenji": ["Fanconi Syndrome", "Progressive Retinal Atrophy"],
    "Basset Fauve de Bretagne": ["Chronic Otitis", "Intervertebral Disc Disease"],
    "Basset Hound": ["Intervertebral Disc Disease", "Chronic Otitis"],
    "Beagle": ["Epilepsy", "Hypothyroidism"],
    "Black and Tan Coonhound": ["Hip Dysplasia", "Chronic Otitis"],
    "Bloodhound": ["Bloat (GDV)", "Chronic Otitis"],
    "Borzoi": ["Bloat (GDV)", "Cardiomyopathy"],
    "Boykin Spaniel": ["Hip Dysplasia", "Progressive Retinal Atrophy"],
    "Brittany": ["Hip Dysplasia", "Epilepsy"],
    "Chesapeake Bay Retriever": ["Hip Dysplasia", "Progressive Retinal Atrophy"],
    "Cocker Spaniel": ["Progressive Retinal Atrophy", "Chronic Otitis"],
    "Dachshund": ["Intervertebral Disc Disease", "Luxating Patella"],
    "English Cocker Spaniel": ["Progressive Retinal Atrophy", "Chronic Otitis"],
    "English Setter": ["Hip Dysplasia", "Deafness"],
    "English Springer Spaniel": ["Hip Dysplasia", "Progressive Retinal Atrophy"],
    "German Shorthaired Pointer": ["Hip Dysplasia", "Bloat (GDV)"],
    "Golden Retriever": ["Hip Dysplasia", "Subvalvular Aortic Stenosis"],
    "Greyhound": ["Bloat (GDV)", "Cardiomyopathy"],
    "Harrier": ["Hip Dysplasia", "Chronic Otitis"],
    "Irish Setter": ["Hip Dysplasia", "Bloat (GDV)"],
    "Irish Wolfhound": ["Bloat (GDV)", "Dilated Cardiomyopathy"],
    "Labrador Retriever": ["Hip Dysplasia", "Progressive Retinal Atrophy"],
    "Nova Scotia Duck Tolling Retriever": ["Hip Dysplasia", "Progressive Retinal Atrophy"],
    "Plott Hound": ["Hip Dysplasia", "Chronic Otitis"],
    "Pointer": ["Hip Dysplasia", "Epilepsy"],
    "Rhodesian Ridgeback": ["Dermoid Sinus", "Hip Dysplasia"],
    "Saluki": ["Cardiomyopathy", "Hyperthyroidism"],
    "Vizsla": ["Hip Dysplasia", "Epilepsy"],
    "Weimaraner": ["Bloat (GDV)", "Hip Dysplasia"],
    "Whippet": ["Cardiomyopathy", "Progressive Retinal Atrophy"],
    "Akita": ["Hip Dysplasia", "Hypothyroidism"],
    "Alaskan Malamute": ["Hip Dysplasia", "Chondrodysplasia"],
    "Anatolian Shepherd Dog": ["Hip Dysplasia", "Entropion"],
    "Australian Cattle Dog": ["Progressive Retinal Atrophy", "Deafness"],
    "Australian Shepherd": ["MDR1 Drug Sensitivity", "Collie Eye Anomaly"],
    "Bearded Collie": ["Hip Dysplasia", "Progressive Retinal Atrophy"],
    "Belgian Malinois": ["Hip Dysplasia", "Epilepsy"],
    "Belgian Sheepdog": ["Hip Dysplasia", "Epilepsy"],
    "Bernese Mountain Dog": ["Hip Dysplasia", "Histiocytic Sarcoma"],
    "Black Russian Terrier": ["Hip Dysplasia", "Progressive Retinal Atrophy"],
    "Boerboel": ["Hip Dysplasia", "Bloat (GDV)"],
    "Border Collie": ["Collie Eye Anomaly", "Epilepsy"],
    "Bouvier des Flandres": ["Hip Dysplasia", "Subaortic Stenosis"],
    "Boxer": ["Boxer Cardiomyopathy (ARVC)", "Mast Cell Tumors"],
    "Bullmastiff": ["Hip Dysplasia", "Bloat (GDV)"],
    "Cardigan Welsh Corgi": ["Intervertebral Disc Disease", "Progressive Retinal Atrophy"],
    "Cane Corso": ["Hip Dysplasia", "Bloat (GDV)"],
    "Collie": ["Collie Eye Anomaly", "MDR1 Drug Sensitivity"],
    "Doberman Pinscher": ["Dilated Cardiomyopathy", "Von Willebrand Disease"],
    "Dogue de Bordeaux": ["Hip Dysplasia", "Bloat (GDV)"],
    "German Shepherd Dog": ["Hip Dysplasia", "Degenerative Myelopathy"],
    "Great Dane": ["Bloat (GDV)", "Dilated Cardiomyopathy"],
    "Great Pyrenees": ["Hip Dysplasia", "Bloat (GDV)"],
    "Greater Swiss Mountain Dog": ["Hip Dysplasia", "Bloat (GDV)"],
    "Komondor": ["Hip Dysplasia", "Bloat (GDV)"],
    "Kuvasz": ["Hip Dysplasia", "Osteochondritis Dissecans"],
    "Mastiff": ["Hip Dysplasia", "Bloat (GDV)"],
    "Newfoundland": ["Hip Dysplasia", "Subvalvular Aortic Stenosis"],
    "Pembroke Welsh Corgi": ["Degenerative Myelopathy", "Intervertebral Disc Disease"],
    "Portuguese Water Dog": ["Hip Dysplasia", "Progressive Retinal Atrophy"],
    "Rottweiler": ["Osteosarcoma", "Hip Dysplasia"],
    "Saint Bernard": ["Hip Dysplasia", "Bloat (GDV)"],
    "Samoyed": ["Hip Dysplasia", "Progressive Retinal Atrophy"],
    "Siberian Husky": ["Hereditary Cataracts", "Corneal Dystrophy"],
    "Standard Schnauzer": ["Hip Dysplasia", "Progressive Retinal Atrophy"],
    "Airedale Terrier": ["Hip Dysplasia", "Hypothyroidism"],
    "American Hairless Terrier": ["Skin Sensitivity (Sunburn Risk)", "Patellar Luxation"],
    "American Staffordshire Terrier": ["Hip Dysplasia", "Cardiomyopathy"],
    "Bedlington Terrier": ["Copper Storage Disease", "Patellar Luxation"],
    "Bichon Frise": ["Patellar Luxation", "Dental Disease"],
    "Boston Terrier": ["Brachycephalic Airway Syndrome", "Cataracts"],
    "Bull Terrier": ["Deafness", "Heart Disease"],
    "Cairn Terrier": ["Patellar Luxation", "Legg-Calve-Perthes Disease"],
    "Chow Chow": ["Hip Dysplasia", "Entropion"],
    "Dalmatian": ["Deafness", "Urinary Stones (Urate)"],
    "Finnish Spitz": ["Patellar Luxation", "Progressive Retinal Atrophy"],
    "Irish Terrier": ["Hyperkeratosis", "Patellar Luxation"],
    "Keeshond": ["Patellar Luxation", "Hypothyroidism"],
    "Lhasa Apso": ["Progressive Retinal Atrophy", "Patellar Luxation"],
    "Miniature Schnauzer": ["Pancreatitis", "Urinary Stones"],
    "Norwich Terrier": ["Patellar Luxation", "Upper Airway Syndrome"],
    "Poodle": ["Addison's Disease", "Progressive Retinal Atrophy"],
    "Rat Terrier": ["Patellar Luxation", "Legg-Calve-Perthes Disease"],
    "Russell Terrier": ["Patellar Luxation", "Lens Luxation"],
    "Schipperke": ["Patellar Luxation", "Legg-Calve-Perthes Disease"],
    "Scottish Terrier": ["Von Willebrand Disease", "Patellar Luxation"],
    "Shar-Pei": ["Familial Shar-Pei Fever", "Entropion"],
    "Shiba Inu": ["Patellar Luxation", "Progressive Retinal Atrophy"],
    "Soft Coated Wheaten Terrier": ["Protein-Losing Nephropathy", "Protein-Losing Enteropathy"],
    "Staffordshire Bull Terrier": ["Hereditary Cataracts", "Patellar Luxation"],
    "Teddy Roosevelt Terrier": ["Patellar Luxation", "Legg-Calve-Perthes Disease"],
    "Tibetan Terrier": ["Progressive Retinal Atrophy", "Hip Dysplasia"],
    "West Highland White Terrier": ["Patellar Luxation", "Skin Allergies (Atopy)"],
}
CAT_BREED_RISKS = {
    "Abyssinian": ["Progressive Retinal Atrophy", "Renal Amyloidosis"],
    "American Shorthair": ["Hypertrophic Cardiomyopathy"],
    "American Wirehair": ["Hypertrophic Cardiomyopathy"],
    "Australian Mist": [],
    "Bombay": ["Brachycephalic Airway Syndrome"],
    "British Shorthair": ["Hypertrophic Cardiomyopathy", "Polycystic Kidney Disease"],
    "Burmese": ["Hypokalemia", "Craniofacial Defect"],
    "Burmilla": [],
    "Chartreux": ["Patellar Luxation"],
    "Colorpoint Shorthair": ["Progressive Retinal Atrophy", "Strabismus (Cross-Eye)"],
    "Egyptian Mau": ["Hypertrophic Cardiomyopathy"],
    "European Burmese": ["Hypokalemia"],
    "Exotic Shorthair": ["Polycystic Kidney Disease", "Brachycephalic Airway Syndrome"],
    "Havana Brown": [],
    "Korat": [],
    "Ocicat": [],
    "Oriental Shorthair": ["Progressive Retinal Atrophy"],
    "Russian Blue": ["Obesity (breed tendency)"],
    "Siamese": ["Progressive Retinal Atrophy", "Feline Asthma"],
    "Singapura": [],
    "Snowshoe": [],
    "Thai": ["Progressive Retinal Atrophy"],
    "Tonkinese": ["Progressive Retinal Atrophy"],
    "Balinese": ["Progressive Retinal Atrophy"],
    "Birman": ["Hypertrophic Cardiomyopathy"],
    "British Longhair": ["Hypertrophic Cardiomyopathy", "Polycystic Kidney Disease"],
    "Himalayan": ["Polycystic Kidney Disease", "Brachycephalic Airway Syndrome"],
    "Javanese": [],
    "Maine Coon": ["Hypertrophic Cardiomyopathy", "Hip Dysplasia"],
    "Norwegian Forest Cat": ["Glycogen Storage Disease IV", "Hypertrophic Cardiomyopathy"],
    "Persian": ["Polycystic Kidney Disease", "Brachycephalic Airway Syndrome"],
    "Ragamuffin": ["Hypertrophic Cardiomyopathy"],
    "Ragdoll": ["Hypertrophic Cardiomyopathy"],
    "Scottish Fold Longhair": ["Osteochondrodysplasia"],
    "Siberian": ["Hypertrophic Cardiomyopathy"],
    "Somali": ["Progressive Retinal Atrophy", "Renal Amyloidosis"],
    "Turkish Angora": ["Deafness (white-coat association)"],
    "Turkish Van": ["Deafness (white-coat association)"],
    "American Bobtail": [],
    "American Curl": ["Ear Canal Sensitivity (curled ear structure)"],
    "Bambino": ["Skin Sensitivity (Sunburn/Temperature)", "Skeletal Issues (short-leg conformation)"],
    "Bengal": ["Progressive Retinal Atrophy", "Hypertrophic Cardiomyopathy"],
    "Chausie": [],
    "Cornish Rex": ["Patellar Luxation", "Thin Bone Structure"],
    "Cymric": ["Manx Syndrome (Spinal/Tail Defects)"],
    "Devon Rex": ["Hereditary Myopathy", "Patellar Luxation"],
    "Donskoy": ["Skin Sensitivity (Sunburn/Temperature)"],
    "Highlander": ["Ear Canal Sensitivity (curled ear structure)"],
    "Japanese Bobtail": [],
    "Kurilian Bobtail": [],
    "LaPerm": [],
    "Lykoi": ["Skin Sensitivity (Partial Hairlessness)"],
    "Manx": ["Manx Syndrome (Spinal/Tail Defects)"],
    "Munchkin": ["Lordosis/Pectus Excavatum (short-leg conformation)"],
    "Peterbald": ["Skin Sensitivity (Sunburn/Temperature)"],
    "Pixiebob": [],
    "Savannah": ["Hypertrophic Cardiomyopathy"],
    "Scottish Fold": ["Hypertrophic Cardiomyopathy", "Polycystic Kidney Disease"],
    "Selkirk Rex": ["Polycystic Kidney Disease"],
    "Sphynx": ["Hypertrophic Cardiomyopathy", "Hereditary Myopathy"],
    "Toyger": [],
}
# Breeds where the defining trait IS a lifelong condition, so every one has it.
BREED_ALWAYS_HAS = {
    "Scottish Fold": "Osteochondrodysplasia: inherited cartilage & joint disease — present in all fold-eared cats",
    "Scottish Fold Longhair": "Osteochondrodysplasia: inherited cartilage & joint disease — present in all fold-eared cats",
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
        entries.append(f"Hereditary risk: none specifically identified for the {breed} breed")

    return entries


def generate_random_pet(pet_name, species, breed):
    """Build a Pet with standard stats for the given species/breed."""
    breeds = DOG_BREEDS if species == "dog" else CAT_BREEDS
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


def build_distribution():
    """One (species, breed) slot per breed in the master list — every breed
    appears exactly once. Shuffled only to randomize which owner/pet name
    pairs with which breed, not which breeds are included."""
    distribution = [("dog", breed) for breed in SEEDED_DOG_BREEDS] + [("cat", breed) for breed in SEEDED_CAT_BREEDS]
    random.shuffle(distribution)
    return distribution


def seed_animals_list():
    """Rebuild data.json from scratch with exactly one patient per breed."""
    distribution = build_distribution()
    total = len(distribution)

    if len(OWNER_NAMES) < total or len(PET_NAMES) < total:
        raise ValueError(
            f"Need at least {total} unique owner/pet names, have {len(OWNER_NAMES)} owners and {len(PET_NAMES)} pets."
        )

    owners = []
    for i in range(total):
        species, breed = distribution[i]
        owner = Owner(OWNER_NAMES[i])
        pet = generate_random_pet(PET_NAMES[i], species, breed)
        owner.add_pet(pet)
        owners.append(owner)

    save_owners_to_json(owners, DATA_PATH)

    dogs = sum(1 for species, _breed in distribution if species == "dog")
    cats = sum(1 for species, _breed in distribution if species == "cat")
    print(f"🏥 CLINIC BUILT! {len(owners)} owners: {dogs} dog breeds, {cats} cat breeds (one patient per breed).")


seed_master_list = seed_animals_list


if __name__ == "__main__":
    seed_animals_list()
