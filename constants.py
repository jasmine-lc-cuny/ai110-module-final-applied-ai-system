"""Shared lookup tables and file paths used across PawPal."""

from pathlib import Path

DATA_PATH = Path("data.json")
CLINIC_DATA_PATH = Path("clinic.json")
UPLOADS_PATH = Path("uploads")
BANNER_DIR = Path("assets") / "banners"
NEW_OWNER_CHOICE = "+ Add new owner"

PAGE_BANNERS = {
    "home": Path("assets") / "homepage.png",
    "grooming": BANNER_DIR / "grooming.png",
    "sitting": BANNER_DIR / "sitting.png",
    "training": BANNER_DIR / "training.png",
    "walking": BANNER_DIR / "walking.png",
    "special_services": BANNER_DIR / "dog_cafe.png",
}

APPOINTMENT_STATUS_COLORS = {
    "Pending": "yellow",
    "Confirmed": "blue",
    "Completed": "green",
    "Cancelled": "red",
}

DOCUMENT_CATEGORIES = [
    "Digital radiography",
    "Dental digital x-ray",
    "In-house laboratory diagnostics",
    "Other",
]

PET_TIMELINE_COLORS = [
    "#3B5BDB",
    "#099268",
    "#E8590C",
    "#C2255C",
    "#6741D9",
    "#0C8599",
    "#E03131",
    "#5C940D",
]

COMMON_TASK_TITLES = [
    "Morning Walk",
    "Afternoon Walk",
    "Evening Walk",
    "Breakfast",
    "Lunch",
    "Dinner",
    "Give Medication",
    "Heartworm Prevention",
    "Vet Appointment",
    "X-Ray",
    "Injection Medication",
    "Injection Vaccine",
    "Injection Subcutaneous",
    "Injection Intramuscular",
    "Injection Intravenous",
    "Blood Work",
    "Surgery",
    "Brush Coat",
    "Wash / Bath",
    "Hair Cut",
    "Trim Nails",
    "Ear Cleaning",
    "Teeth Brushing",
    "Playtime",
]

VETERINARY_TASK_REASONS = {
    "Give Medication": ["Heartworm Prevention", "Antibiotics"],
    "X-Ray": ["Hip"],
    "Blood Work": [
        "Complete Blood Count (CBC)",
        "Serum Chemistry",
        "Thyroid Panel",
        "Electrolyte Panel",
        "Pre-Anesthetic Panel",
        "Coagulation Profile",
    ],
    "Injection Subcutaneous": [
        "Routine Vaccines",
        "Maintenance Medications (e.g. Insulin)",
        "Fluid Therapy",
    ],
    "Injection Intramuscular": [
        "Pain Management",
        "Sedatives and Tranquilizers",
        "Antibiotics",
    ],
    "Injection Intravenous": [
        "General Anesthesia",
        "Emergency Medications",
        "Chemotherapy",
        "Continuous Fluid Therapy",
    ],
}

VETERINARY_TASK_REASONS_BY_SPECIES = {
    "Injection Vaccine": {
        "dog": ["Rabies", "Distemper", "Parvovirus", "Adenovirus"],
        "cat": ["Rabies", "Panleukopenia", "Calicivirus", "Herpesvirus"],
    },
    "Surgery": {
        "dog": [
            "Neuter",
            "Dental Extractions",
            "Mass/Tumor Removals",
            "Gastrointestinal Surgeries",
            "Exploratory Laparotomy",
            "C-Section",
        ],
        "cat": [
            "Spay",
            "Dental Extractions",
            "Mass/Tumor Removals",
            "Gastrointestinal Surgeries",
            "Exploratory Laparotomy",
            "C-Section",
        ],
    },
}

INJECTION_MEDICATION_CATEGORIES = [
    "Pain & Arthritis Management",
    "Flea, Tick, & Allergy Relief",
    "Antibiotics & General Treatment",
]

INJECTION_MEDICATION_PAIN_OPTIONS_BY_SPECIES = {
    "dog": ["Librela (bedinvetmab)", "Adequan Canine (polysulfated glycosaminoglycan)"],
    "cat": ["Solensia (frunevetmab)"],
}

INJECTION_MEDICATION_OPTIONS = {
    "Flea, Tick, & Allergy Relief": ["Bravecto Quantum", "Cytopoint"],
    "Antibiotics & General Treatment": ["Convenia (cefovecin sodium)", "Injectable Insulin (Vetsulin or ProZinc)"],
}

A_LA_BARK_MENU = [
    (
        "🍔 Pooch Pub Grub",
        "Hearty, warm, and savory meals for the hungriest pups.",
        [
            ("Mini Paw Burger & Sliders", "$6.50", "Small beef patties served with a side of steamed veggies."),
            ("The Bark-B-Q Platter", "$8.50", "Slow-cooked, shredded chicken or beef with a drizzle of dog-safe bone broth."),
            ("Shepherd’s Pie for Paws", "$7.25", "Lean ground meat topped with a layer of mashed sweet potato and peas."),
            ("Barkingly Good Beef Supper", "$5.00", "A warm meal of ground beef, brown rice, and vegetables."),
            ("Waggingly Delicious Chicken Dinner", "$5.00", "Slow-cooked chicken in doggy gravy with crushed potatoes and vegetables."),
            ("Doggy Bowl", "$7.00", "A full meal featuring turkey, brown rice, corn, peas, green beans, and carrots."),
        ],
    ),
    (
        "🧁 Poodings & Paws-tisserie",
        "Sweet, decadent treats and baked goods to finish off the perfect outing.",
        [
            ("Pup-Cake Delight", "$3.75", "A single-serve cupcake topped with sugar-free yogurt icing and a biscuit crumble."),
            ("Pupcake", "$3.20", "A classic baked treat."),
            ("Doggy Doughnut", "$3.20", "A sweet ring-shaped baked good."),
            ("Doggy Éclair", "$3.84", "A specialty pastry-style treat."),
            ("Iced Bone", "$3.20", "A crunchy, frosted biscuit bone."),
        ],
    ),
    (
        "🍦 Frosty Furs & Chillers",
        "Refreshing, icy, and creamy delights for hot days.",
        [
            ("Bark-A-Licious Gelato", "$4.50", "A generous scoop of peanut butter or banana-flavored doggy ice cream."),
            ("Frosty Paws Ice Cream Cup", "$4.99", "A cool, wholesome treat containing essential vitamins, minerals, and protein."),
            ("Whipped Cream \"Pup-Tini\"", "$2.50", "A small, fluffy cup of fresh whipped cream served with a crunchy bone-shaped cookie."),
            ("Doggie Frap", "$1.89", "A small bowl of homemade whipped cream."),
            ("Puppuccino", "$2.56", "A bowl of freshly chilled goat’s milk."),
        ],
    ),
    (
        "🦴 Snack-Attack Nibbles",
        "Small, quick bites perfect for training or snacking.",
        [
            ("Lil' Nibbles", "$0.63–$3.19", "Smaller snacks including chicken breast, sausages, biscuits, or a Yorkie puddin'."),
            ("Veggie Snacks", "$3.00", "A healthy mix of apples, carrots, and cucumbers."),
            ("Scooby Snacks", "$4.00", "A treat made with pumpkin, peanut butter, milk, and oats."),
            ("Bon A-Pet Treat", "$2.00", "Homemade peanut butter bone-shaped biscuits."),
        ],
    ),
    (
        "🍺 The Wet Bar (For Canines)",
        "Non-alcoholic, dog-safe beverages.",
        [
            ("Dog Beer", "$3.84", "A refreshing, non-alcoholic brew."),
            ("Bottom Sniffer Beer", "$4.93", "A specialized doggy beer."),
            ("Pawsacco", "$3.84", "A specialized herbal blend."),
            ("Doggy Afternoon Tea", "$8.96", "Specialized blends for oral health or skin and coat support."),
        ],
    ),
]

SERVICE_SECTIONS = [
    ("🛁", "Grooming"),
    ("🏠", "Sitting"),
    ("🎓", "Training"),
    ("🐕", "Walking"),
    ("🍖", "Dog Cafes"),
]

COMMON_SERVICES = [
    ("Blood Work", 45.0),
    ("X-Ray", 100.0),
    ("Checkup", 75.0),
    ("Vaccination", 65.0),
    ("Dental Cleaning", 180.0),
    ("Spay/Neuter", 250.0),
]

SERVICE_CATEGORY_ICONS = {
    "grooming": {"👂", "🦷", "💅", "✂️", "🧼", "🪮"},
    "walking": {"🐕"},
    "sitting": {"🏠"},
    "training": {"🎓"},
    "veterinary": {"💊", "🏥"},
    "special_services": {"🍖", "🐾"},
}

CATEGORY_TASK_TITLES = {
    "grooming": ["Brush Coat", "Wash / Bath", "Hair Cut", "Trim Nails", "Ear Cleaning", "Teeth Brushing"],
    "walking": ["Morning Walk", "Afternoon Walk", "Evening Walk", "Playtime"],
    "sitting": ["Day Sitting", "Overnight Sitting", "Drop-In Visit", "House Sitting"],
    "training": ["Obedience Training", "Puppy Class", "Leash Training", "Trick Training"],
    "veterinary": [
        "Give Medication",
        "Heartworm Prevention",
        "Vet Appointment",
        "X-Ray",
        "Injection Medication",
        "Injection Vaccine",
        "Injection Subcutaneous",
        "Injection Intramuscular",
        "Injection Intravenous",
        "Blood Work",
        "Surgery",
    ],
    "special_services": ["Breakfast", "Lunch", "Dinner"],
}

CATEGORY_TO_SECTION = {
    "grooming": "Grooming",
    "sitting": "Sitting",
    "training": "Training",
    "walking": "Walking",
    "special_services": "Dog Cafes",
}

# (duration_minutes, priority, frequency) defaults per category — shared by
# the seeder and the agentic booking planner so both use the same durations.
CATEGORY_TASK_DEFAULTS = {
    "walking": (30, "medium", "daily"),
    "grooming": (25, "medium", "once"),
    "training": (45, "high", "once"),
    "special_services": (15, "medium", "daily"),
    "sitting": (60, "medium", "once"),
}
