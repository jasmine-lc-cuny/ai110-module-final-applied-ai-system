"""Breed personality trait lookup.

Personality is a fixed property of the breed itself, not the individual
pet, so it lives here as a single lookup table instead of being generated
and stored per-Pet (the same reasoning as grooming_duration.py deriving
duration from breed rather than mutating pet data).
"""

from __future__ import annotations

from seed.seed_animals_distribution import (
    CAT_BREEDS_LONGHAIR_FLUFFY,
    CAT_BREEDS_SHORTHAIR_TRADITIONAL,
    CAT_BREEDS_UNIQUE_MUTATIONS,
    DOG_BREEDS_COMPANION_TOY,
    DOG_BREEDS_SPORTING_HOUND,
    DOG_BREEDS_TERRIER_NONSPORTING,
    DOG_BREEDS_WORKING_HERDING,
)

DOG_BREED_GROUPS: dict[str, list[str]] = {
    "Companion & Toy": DOG_BREEDS_COMPANION_TOY,
    "Sporting & Hound": DOG_BREEDS_SPORTING_HOUND,
    "Working & Herding": DOG_BREEDS_WORKING_HERDING,
    "Terrier & Non-Sporting": DOG_BREEDS_TERRIER_NONSPORTING,
}

CAT_BREED_GROUPS: dict[str, list[str]] = {
    "Shorthair & Traditional": CAT_BREEDS_SHORTHAIR_TRADITIONAL,
    "Longhair & Fluffy": CAT_BREEDS_LONGHAIR_FLUFFY,
    "Unique Mutations": CAT_BREEDS_UNIQUE_MUTATIONS,
}

DOG_BREED_PERSONALITIES: dict[str, str] = {
    # Companion & Toy
    "Affenpinscher": "Confident, funny, loyal, and fiercely affectionate.",
    "Biewer Terrier": "Cheerful, charming, playful, and highly energetic.",
    "Bolognese": "Playful, easygoing, devoted, and very attached to owners.",
    "Brussels Griffon": "Alert, curious, sensitive, and full of self-importance.",
    "Cavalier King Charles Spaniel": "Affectionate, gentle, graceful, and highly adaptable.",
    "Chihuahua": "Charming, sassy, bold, and fiercely loyal.",
    "Chinese Crested": "Lively, alert, affectionate, and deeply devoted.",
    "English Toy Spaniel": "Mellow, playful, gentle, and quietly loving.",
    "French Bulldog": "Adaptable, playful, smart, and completely irresistible.",
    "Havanese": "Intelligent, outgoing, funny, and highly social.",
    "Italian Greyhound": "Sensitive, playful, alert, and deeply affectionate.",
    "Japanese Chin": "Cat-like, noble, quiet, and intensely loving.",
    "Maltese": "Gentle, fearless, playful, and deeply sweet.",
    "Miniature Pinscher": "Fearless, energetic, proud, and intensely alert.",
    "Papillon": "Happy, alert, friendly, and surprisingly athletic.",
    "Pekingese": "Independent, opinionated, loyal, and quietly regal.",
    "Pomeranian": "Lively, bold, curious, and highly vocal.",
    "Pug": "Mischievous, loving, even-tempered, and highly charming.",
    "Russian Tsvetnaya Bolonka": "Friendly, clever, sturdy, and highly sociable.",
    "Shih Tzu": "Affectionate, playful, outgoing, and deeply sweet-natured.",
    "Toy Poodle": "Agile, intelligent, highly energetic, and proud.",
    "Yorkshire Terrier": "Feisty, brave, energetic, and highly affectionate.",
    # Sporting & Hound
    "Afghan Hound": "Independent, aloof, elegant, and deeply dignified.",
    "American Water Spaniel": "Eager, energetic, friendly, and highly trainable.",
    "Basenji": "Independent, smart, quiet, and intensely alert.",
    "Basset Fauve de Bretagne": "Smart, courageous, determined, and highly energetic.",
    "Basset Hound": "Patient, low-key, charming, and stubbornly independent.",
    "Beagle": "Merry, friendly, curious, and incredibly vocal.",
    "Black and Tan Coonhound": "Even-tempered, easygoing, independent, and focused.",
    "Bloodhound": "Gentle, patient, independent, and relentlessly stubborn.",
    "Borzoi": "Quiet, calm, independent, and deeply loyal.",
    "Boykin Spaniel": "Eager, friendly, energetic, and a dedicated worker.",
    "Brittany": "Bright, upbeat, athletic, and highly trainable.",
    "Chesapeake Bay Retriever": "Affectionate, protective, bright, and deeply athletic.",
    "Cocker Spaniel": "Gentle, happy, smart, and eager to please.",
    "Dachshund": "Clever, brave, stubborn, and highly lively.",
    "English Cocker Spaniel": "Energetic, cheerful, adaptable, and deeply sweet.",
    "English Setter": "Merry, gentle, friendly, and placidly mellow.",
    "English Springer Spaniel": "Playful, obedient, friendly, and highly active.",
    "German Shorthaired Pointer": "Friendly, smart, willing, and explosively energetic.",
    "Golden Retriever": "Intelligent, friendly, devoted, and incredibly enthusiastic.",
    "Greyhound": "Gentle, independent, quiet, and a natural couch potato.",
    "Harrier": "Outgoing, friendly, active, and highly pack-oriented.",
    "Irish Setter": "Active, outgoing, sweet-tempered, and highly playful.",
    "Irish Wolfhound": "Calm, dignified, gentle, and quietly courageous.",
    "Labrador Retriever": "Outgoing, friendly, active, and highly adaptable.",
    "Nova Scotia Duck Tolling Retriever": "Outgoing, smart, affectionate, and tirelessly energetic.",
    "Plott Hound": "Alert, confident, brave, and deeply loyal.",
    "Pointer": "Even-tempered, alert, active, and highly driven.",
    "Rhodesian Ridgeback": "Dignified, strong-willed, independent, and quietly protective.",
    "Saluki": "Gentle, dignified, independent, and quietly aloof.",
    "Vizsla": "Affectionate, energetic, sensitive, and deeply attached (\"velcro\").",
    "Weimaraner": "Friendly, fearless, alert, and intensely active.",
    "Whippet": "Calm, gentle, playful, and quietly affectionate.",
    # Working & Herding
    "Akita": "Courageous, dignified, independent, and fiercely loyal.",
    "Alaskan Malamute": "Affectionate, loyal, playful, and highly independent.",
    "Anatolian Shepherd Dog": "Protective, independent, calm, and deeply dedicated.",
    "Australian Cattle Dog": "Alert, curious, highly intelligent, and watchful.",
    "Australian Shepherd": "Smart, work-oriented, exuberant, and highly adaptable.",
    "Bearded Collie": "Bouncy, charismatic, smart, and highly energetic.",
    "Belgian Malinois": "Confident, hardworking, intensely alert, and protective.",
    "Belgian Sheepdog": "Watchful, devoted, highly protective, and intelligent.",
    "Bernese Mountain Dog": "Good-natured, calm, strong, and deeply affectionate.",
    "Black Russian Terrier": "Calm, confident, courageous, and deeply protective.",
    "Boerboel": "Confident, dominant, protective, and intensely loyal.",
    "Border Collie": "Workaholic, highly intelligent, energetic, and alert.",
    "Bouvier des Flandres": "Courageous, protective, gentle, and deeply loyal.",
    "Boxer": "Fun-loving, active, bright, and fiercely protective.",
    "Bullmastiff": "Brave, affectionate, loyal, and quietly confident.",
    "Cardigan Welsh Corgi": "Loyal, affectionate, smart, and highly alert.",
    "Cane Corso": "Smart, trainable, assertive, and fiercely protective.",
    "Collie": "Devoted, graceful, proud, and highly intelligent.",
    "Doberman Pinscher": "Alert, fearless, loyal, and highly intelligent.",
    "Dogue de Bordeaux": "Loyal, affectionate, calm, and naturally protective.",
    "German Shepherd Dog": "Courageous, intelligent, versatile, and fiercely loyal.",
    "Great Dane": "Friendly, patient, dependable, and a gentle giant.",
    "Great Pyrenees": "Patient, independent, calm, and fiercely protective.",
    "Greater Swiss Mountain Dog": "Faithful, dependable, active, and family-oriented.",
    "Komondor": "Dignified, independent, protective, and calm.",
    "Kuvasz": "Fiercely protective, loyal, independent, and courageous.",
    "Mastiff": "Courageous, monumental, dignified, and a gentle giant.",
    "Newfoundland": "Sweet, patient, devoted, and naturally protective.",
    "Pembroke Welsh Corgi": "Affectionate, smart, alert, and highly energetic.",
    "Portuguese Water Dog": "Loving, independent, smart, and highly athletic.",
    "Rottweiler": "Loyal, loving, confident, and a natural guardian.",
    "Saint Bernard": "Friendly, patient, calm, and deeply gentle.",
    "Samoyed": "Adaptable, friendly, gentle, and highly social.",
    "Siberian Husky": "Mischievous, outgoing, loyal, and highly independent.",
    "Standard Schnauzer": "Smart, high-spirited, fearless, and deeply protective.",
    # Terrier & Non-Sporting
    "Airedale Terrier": "Clever, courageous, friendly, and highly energetic.",
    "American Hairless Terrier": "Energetic, alert, curious, and deeply affectionate.",
    "American Staffordshire Terrier": "Confident, smart, good-natured, and intensely loyal.",
    "Bedlington Terrier": "Charming, graceful, alert, and surprisingly spunky.",
    "Bichon Frise": "Playful, curious, cheerful, and highly social.",
    "Boston Terrier": "Friendly, lively, amusing, and highly adaptable.",
    "Bull Terrier": "Playful, mischievous, energetic, and intensely stubborn.",
    "Cairn Terrier": "Alert, independent, cheerful, and busy.",
    "Chow Chow": "Dignified, bright, independent, and fiercely aloof.",
    "Dalmatian": "Dignified, outgoing, smart, and highly athletic.",
    "Finnish Spitz": "Friendly, energetic, alert, and famously vocal.",
    "Irish Terrier": "Bold, energetic, loyal, and deeply courageous.",
    "Keeshond": "Outgoing, cheerful, friendly, and a natural companion.",
    "Lhasa Apso": "Independent, joyful, mischievous, and quietly aloof.",
    "Miniature Schnauzer": "Friendly, smart, obedient, and highly alert.",
    "Norwich Terrier": "Affectionate, energetic, hungry for adventure, and brave.",
    "Poodle": "Highly intelligent, active, proud, and adaptable.",
    "Rat Terrier": "Friendly, energetic, curious, and highly alert.",
    "Russell Terrier": "Alert, lively, inquisitive, and relentlessly driven.",
    "Schipperke": "Curious, intensive, alert, and fiercely independent.",
    "Scottish Terrier": "Independent, confident, dignified, and proudly aloof.",
    "Shar-Pei": "Independent, loyal, quiet, and naturally suspicious.",
    "Shiba Inu": "Alert, active, cat-like, and fiercely independent.",
    "Soft Coated Wheaten Terrier": "Happy, friendly, deeply affectionate, and stubborn.",
    "Staffordshire Bull Terrier": "Brave, tenacious, playful, and deeply patient.",
    "Teddy Roosevelt Terrier": "Clever, loyal, active, and highly protective.",
    "Tibetan Terrier": "Affectionate, sensitive, clever, and vocal.",
    "West Highland White Terrier": "Happy, smart, loyal, and full of attitude.",
}

CAT_BREED_PERSONALITIES: dict[str, str] = {
    # Shorthair & Traditional
    "Abyssinian": "Active, curious, highly playful, and dynamic.",
    "American Shorthair": "Gentle, adaptable, quiet, and an excellent hunter.",
    "American Wirehair": "Even-tempered, loving, playful, and highly quiet.",
    "Australian Mist": "Friendly, gentle, adaptable, and loves laps.",
    "Bombay": "Outgoing, demanding, intelligent, and highly affectionate.",
    "British Shorthair": "Calm, easygoing, dignified, and quietly loyal.",
    "Burmese": "People-oriented, demanding, playful, and vocal.",
    "Burmilla": "Sociable, playful, affectionate, and gently quiet.",
    "Chartreux": "Calm, quiet, gentle, and an excellent observer.",
    "Colorpoint Shorthair": "Vocal, active, highly demanding, and intelligent.",
    "Egyptian Mau": "Active, fiercely loyal, athletic, and gentle.",
    "European Burmese": "Intelligent, highly affectionate, energetic, and talkative.",
    "Exotic Shorthair": "Sweet, quiet, peaceful, and quietly playful.",
    "Havana Brown": "Curious, demanding, affectionate, and highly charming.",
    "Korat": "Quiet, gentle, highly perceptive, and devoted.",
    "Ocicat": "Outgoing, active, highly social, and dog-like.",
    "Oriental Shorthair": "Chatty, intelligent, highly demanding, and active.",
    "Russian Blue": "Quiet, reserved, deeply loyal, and gentle.",
    "Siamese": "Extremely vocal, intelligent, demanding, and affectionate.",
    "Singapura": "Tiny, high-energy, mischievous, and intensely curious.",
    "Snowshoe": "Vocal, affectionate, intelligent, and loves water.",
    "Thai": "Outgoing, deeply affectionate, vocal, and highly intelligent.",
    "Tonkinese": "Vocal, playful, highly affectionate, and social.",
    # Longhair & Fluffy
    "Balinese": "Playful, vocal, highly affectionate, and intelligent.",
    "Birman": "Sweet, gentle, quiet, and highly loving.",
    "British Longhair": "Calm, independent, easygoing, and quietly affectionate.",
    "Himalayan": "Sweet, serene, quiet, and prefers calm spaces.",
    "Javanese": "Vocal, playful, highly active, and clever.",
    "Maine Coon": "Friendly, gentle giant, playful, and highly adaptable.",
    "Norwegian Forest Cat": "Independent, secure, loving, and a natural climber.",
    "Persian": "Sweet, calm, quiet, and prefers a steady environment.",
    "Ragamuffin": "Sweet, docile, cuddly, and deeply patient.",
    "Ragdoll": "Placid, affectionate, gentle, and goes limp when held.",
    "Scottish Fold Longhair": "Loving, quiet, adaptable, and loves resting on its back.",
    "Siberian": "Adventurous, intelligent, agile, and deeply affectionate.",
    "Somali": "Active, alert, playful, and highly clever.",
    "Turkish Angora": "Playful, intelligent, active, and a natural leader.",
    "Turkish Van": "Energetic, highly active, independent, and famously loves water.",
    # Unique Mutations
    "American Bobtail": "Loving, intelligent, dog-like, and highly adaptable.",
    "American Curl": "Friendly, playful, inquisitive, and highly social.",
    "Bambino": "Energetic, mischievous, affectionate, and highly outgoing.",
    "Bengal": "Wildly energetic, highly intelligent, agile, and talkative.",
    "Chausie": "Fearless, highly athletic, active, and intelligent.",
    "Cornish Rex": "Energetic, highly playful, affectionate, and acrobatic.",
    "Cymric": "Sweet, playful, active, and a skilled jumper.",
    "Devon Rex": "Mischievous, active, clown-like, and intensely social.",
    "Donskoy": "Loyal, friendly, highly affectionate, and social.",
    "Highlander": "Playful, powerful, loving, and highly athletic.",
    "Japanese Bobtail": "Active, intelligent, chatty, and loves playing fetch.",
    "Kurilian Bobtail": "Clever, independent, friendly, and an agile hunter.",
    "LaPerm": "Outgoing, active, highly affectionate, and gentle.",
    "Lykoi": "Independent, intense hunter instinct, yet deeply loyal and friendly.",
    "Manx": "Quiet, playful, intelligent, and highly protective.",
    "Munchkin": "Outgoing, fast-moving, playful, and intensely curious.",
    "Peterbald": "Sweet, peaceful, highly demanding, and social.",
    "Pixiebob": "Quiet, active, highly trainable, and dog-like.",
    "Savannah": "Highly athletic, demanding, active, and fiercely smart.",
    "Scottish Fold": "Loving, clever, quiet, and adaptable.",
    "Selkirk Rex": "Patient, loving, quiet, and intensely cuddly.",
    "Sphynx": "Energetic, clownish, demanding, and highly affectionate.",
    "Toyger": "Outgoing, friendly, active, and highly trainable.",
}


def breed_personality(species: str, breed: str | None) -> str | None:
    """Look up the personality blurb for a breed, or None if unknown."""
    if not breed:
        return None
    table = DOG_BREED_PERSONALITIES if species == "dog" else CAT_BREED_PERSONALITIES
    return table.get(breed)


def breed_group(species: str, breed: str | None) -> str | None:
    """Look up which breed group (e.g. 'Sporting & Hound') a breed belongs to."""
    if not breed:
        return None
    groups = DOG_BREED_GROUPS if species == "dog" else CAT_BREED_GROUPS
    for group_name, breeds in groups.items():
        if breed in breeds:
            return group_name
    return None
