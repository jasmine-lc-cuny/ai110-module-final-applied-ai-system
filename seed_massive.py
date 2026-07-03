import random
from pawpal_system import Owner, Pet, load_owners_from_json, save_owners_to_json
from pathlib import Path

DATA_PATH = "data.json"

OWNER_NAMES = [
    "Liam Gallagher", "Emma Thompson", "Noah Williams", "Olivia Brown", "William Jones",
    "Ava Garcia", "James Martinez", "Isabella Robinson", "Oliver Clark", "Sophia Rodriguez",
    "Benjamin Lewis", "Mia Lee", "Elijah Walker", "Charlotte Hall", "Lucas Allen",
    "Amelia Young", "Mason King", "Harper Wright", "Logan Scott", "Evelyn Torres",
    "Alexander Nguyen", "Abigail Hill", "Ethan Flores", "Emily Green", "Jacob Adams",
    "Elizabeth Nelson", "Michael Baker", "Mila Rivera", "Daniel Campbell", "Ella Mitchell",
    "Henry Carter", "Avery Roberts", "Jackson Gomez", "Sofia Phillips", "Sebastian Evans",
    "Camila Turner", "Aiden Diaz", "Aria Parker", "Matthew Cruz", "Scarlett Edwards",
    "Samuel Collins", "Victoria Reyes", "David Stewart", "Madison Morris", "Joseph Morales",
    "Luna Murphy", "Carter Cook", "Grace Rogers", "Owen Gutierrez", "Chloe Ortiz",
    "Wyatt Morgan", "Penelope Cooper", "John Peterson", "Layla Bailey", "Luke Reed",
    "Zoe Jenkins", "Levi Ward", "Stella Brooks", "Gabriel Kelly", "Nora Sanders"
]

PET_NAMES = [
    "Nibbles", "Shadow", "Pippin", "Gizmo", "Luna", "Spike", "Bubbles", "Rex", "Ziggy", "Mango",
    "Kiwi", "Yoshi", "Draco", "Finn", "Nemo", "Dory", "Mochi", "Peanut", "Barnaby", "Thor",
    "Cleo", "Jasper", "Ruby", "Oreo", "Simba", "Coco", "Bandit", "Apollo", "Rocky", "Hazel",
    "Penny", "Blue", "Pepper", "Oscar", "Dexter", "Toby", "Winston", "Olive", "Lily", "Daisy",
    "Milo", "Leo", "Loki", "Chester", "Felix", "Sunny", "Pumpkin", "Rosie", "Archie", "Willow",
    "Max", "Bella", "Charlie", "Lucy", "Cooper", "Buster", "Riley", "Tucker", "Murphy", "Roxy"
]

EXOTIC_SMALL_PETS = ["rabbit", "bunny", "hamster", "gerbil", "mouse", "mice", "rat", "chinchilla", "guinea pig", "ferret", "hedgehog", "sugar glider", "squirrel"]
EXOTIC_AVIAN = ["budgie", "canary", "finch", "parrot", "cockatiel", "conure", "chicken", "duck", "goose", "pigeon", "owl", "falcon", "snowy owl"]
REPTILES = ["bearded dragon", "leopard gecko", "crested gecko", "chameleon", "iguana", "skink", "turtle", "tortoise", "corn snake", "ball python", "king snake", "frog", "toad", "newt", "salamander"]
FISH = ["betta", "guppy", "platy", "swordtail", "molly", "tetra", "goldfish", "danio", "minnow", "cichlid", "pleco", "clownfish", "damselfish", "goby", "blenny"]

def generate_random_exotic(pet_name):
    category = random.choice(["mammal", "avian", "reptile", "fish"])
    if category == "mammal":
        species = random.choice(EXOTIC_SMALL_PETS)
        return Pet(
            name=pet_name, species=species, age=random.randint(1, 5), sex=random.choice(["Male", "Female"]),
            weight=f"{random.randint(1, 5)} lbs", height="Small", color_markings=random.choice(["Agouti", "White", "Black", "Spotted", "Albino"]),
            spayed_neutered=random.choice(["Yes", "No"]), diet_good=["Timothy Hay", "Pellets", "Fresh Veggies"], diet_bad=["Sugary fruits", "Seeds"]
        )
    elif category == "avian":
        species = random.choice(EXOTIC_AVIAN)
        return Pet(
            name=pet_name, species=species, age=random.randint(1, 20), sex=random.choice(["Male", "Female"]),
            weight=f"{random.randint(50, 500)} g", height=f"Wingspan: {random.randint(10, 30)} inches", 
            color_markings=random.choice(["Green", "Blue", "Yellow", "White", "Multi-colored"]),
            microchip_number=f"Leg Band # {random.randint(1000,9999)}", diet_good=["Seeds", "Pellets", "Fresh Fruit"], diet_bad=["Avocado", "Chocolate"]
        )
    elif category == "reptile":
        species = random.choice(REPTILES)
        return Pet(
            name=pet_name, species=species, age=random.randint(1, 15), sex=random.choice(["Male", "Female"]),
            weight=f"{random.randint(50, 1000)} g", color_markings=random.choice(["Green", "Brown", "Orange Morph", "Striped"]),
            allergies=f"Enclosure Temp: {random.randint(75, 95)}°F", diet_good=["Insects", "Leafy Greens", "Worms"], diet_bad=["Fireflies", "Iceberg Lettuce"]
        )
    elif category == "fish":
        species = random.choice(FISH)
        return Pet(
            name=pet_name, species=species, age=random.randint(1, 5), sex="Unknown",
            weight=f"Tank Size: {random.choice([10, 20, 30, 50, 100])} Gallons", color_markings=random.choice(["Iridescent", "Neon", "Red", "Blue", "Striped"]),
            blood_type=random.choice(["Freshwater", "Saltwater / Marine"]), diet_good=["Flakes", "Bloodworms", "Brine Shrimp"], diet_bad=["Wrong water type"]
        )

def seed_massive():
    if Path(DATA_PATH).exists():
        owners = load_owners_from_json(DATA_PATH)
    else:
        owners = []
    existing_owner_names = {o.name for o in owners}
    new_owners = []
    for i, owner_name in enumerate(OWNER_NAMES):
        if owner_name not in existing_owner_names:
            owner = Owner(owner_name)
            pet = generate_random_exotic(PET_NAMES[i % len(PET_NAMES)])
            owner.add_pet(pet)
            new_owners.append(owner)
    owners.extend(new_owners)
    save_owners_to_json(owners, DATA_PATH)
    print(f"Successfully seeded {len(new_owners)} NEW exotic pet owners! Total owners in database: {len(owners)}.")

if __name__ == "__main__":
    seed_massive()
