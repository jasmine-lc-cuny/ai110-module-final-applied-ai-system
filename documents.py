"""File-upload helpers for attaching documents to a pet's record."""

import re
import uuid
from pathlib import Path

from constants import UPLOADS_PATH
from pawpal_system import Document, Owner, Pet


def slugify_for_path(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return slug or "unnamed"


def save_uploaded_document(owner: Owner, pet: Pet, category: str, uploaded_file) -> Document:
    pet_dir = UPLOADS_PATH / f"{slugify_for_path(owner.name)}__{slugify_for_path(pet.name)}"
    pet_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex[:8]}_{uploaded_file.name}"
    stored_path = pet_dir / stored_name
    with open(stored_path, "wb") as file:
        file.write(uploaded_file.getbuffer())
    return Document(category=category, filename=uploaded_file.name, path=str(stored_path))


def delete_uploaded_document(document: Document) -> None:
    Path(document.path).unlink(missing_ok=True)
