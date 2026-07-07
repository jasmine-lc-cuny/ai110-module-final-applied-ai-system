# Model Card: PawPal+ Applied AI System

## Model Name

PawPal+ Applied AI System

## Intended Use

PawPal+ is a classroom portfolio project that combines a pet-care scheduler with a local retrieval-backed advice layer. It is intended to demonstrate an applied AI system that uses retrieval-augmented guidance, confidence scoring, logging, and guardrails.

## How The System Works

The base app manages pets, tasks, recurring routines, and conflict warnings. The applied AI layer retrieves guidance from a local corpus before making booking suggestions, then returns a recommendation, a short explanation, and a confidence score. The app uses that advice to preselect task options and show users why the choice was suggested.

Each booking form also has an agentic planner (`ai_applied_agentic_loop.py`, "🤖 Run Auto-Planner"). Where the retrieval layer above is a single retrieve-then-respond call, the planner is a multi-step loop: it retrieves guidance, proposes a staff member and time slot, checks that proposal against the pet's own existing schedule, and revises — trying the next slot or staff member — if it finds a conflict, before finally setting the form's own staff/time widgets to its choice. Every step of that reasoning is logged to `logs/agent_traces.jsonl`; example traces are in `ai_interactions.md`.

The Veterinarian section also has an AI Pre-Diagnostic Assessment page (`ai_applied_prediagnostic.py`). An owner describes a pet's symptoms, and the system retrieves a matching specialty from its own corpus (`data/symptom_guides.csv`), then recommends a specific active doctor in that department — checking the doctor's real schedule for an open slot today and escalating to the next matching doctor if the first is fully booked. One symptom guardrail here is actual enforced code rather than descriptive text: a hardcoded list of emergency keywords overrides the normal match entirely, always routing to Emergency care regardless of anything else typed. The recommendation is never a diagnosis — it only routes the owner toward a specialist and hands its choice to the existing booking flow.

There is also an AI Medication Advisor page (`ai_applied_medication_advisor.py`). Given a pet's already-diagnosed condition, it retrieves a matching medication from a curated corpus of real label indications (`data/medication_guides.csv`) — never a dose, and never a species the entry doesn't list. Species is a hard filter applied before scoring, not a bonus, so a medication can't be suggested for the wrong species even if its keywords otherwise match well. Each entry is also honestly tagged with whether it's actually FDA-approved for animal use or an off-label human drug used under veterinary direction, rather than presenting every entry as equally "labeled."

The "PawPal AI Pet Adoption" section adds an Adoption Match Quiz (`ai_applied_adoption_match.py`). It scores every seeded breed against 4 lifestyle answers (energy level, grooming tolerance, apartment size, kid-friendliness) using a new structured trait table (`breed_traits.py`), and returns the top 5 with a plain-language match label and a per-axis reasoning trace. It also shows mock "available now" adoption listings alongside the results — these are clearly-labeled synthetic demo data (deterministically generated from the breed name), never written to the app's real patient data, and never presented as an actual shelter's current inventory.

## Data

The retrieval corpus is intentionally small and local. It contains service guidance for grooming, sitting, training, walking, dog cafe, and veterinary scenarios. That makes the system easy to inspect and reproduce, but it also limits coverage.

## Limitations and Biases

The advice layer uses simple keyword-style retrieval, so it can miss unusual phrasing or synonyms. The guidance is generic and cannot replace professional veterinary judgment or user-specific context. Because the corpus is handcrafted, the output can reflect the assumptions and priorities of the project author.

## Possible Misuse and Prevention

The app could be misused if someone treated the advice as medical certainty or as a substitute for professional care. This risk is highest in the AI Pre-Diagnostic Assessment and AI Medication Advisor, since both explicitly discuss symptoms, diagnoses, and medications — so neither is ever presented as a diagnosis or prescription, both always show a guardrail disclaimer alongside their recommendation, and the medication advisor never states a dose at all. The pre-diagnostic assessment's hardcoded emergency-keyword check routes a potentially life-threatening symptom to Emergency care rather than silently letting it be outscored by an unrelated keyword, and the medication advisor's hardcoded species filter never suggests a medication for the wrong species, even if it would otherwise score highest. The Adoption Match Quiz's mock "available now" listings could be misread as real shelter inventory if not clearly labeled, so every place they render carries a fixed "demo listings, for illustration only" caption — actual enforced code, not a note the user has to notice on their own. Beyond that, the system keeps all advice narrow, shows guardrail text, and preserves the user as the final decision-maker.

## Reliability Testing

I tested the system with both the PawPal backend tests and an applied-AI evaluation script. The tests check the original scheduling features as well as whether the AI retrieval layer loads and affects the UI flow. Logging writes each advice run to JSONL so the behavior can be inspected later.

## What Surprised Me

I expected the keyword-scoring retrieval to need tie-breaking logic for edge cases, but in practice the category-match weight (2.0) dominates enough that species and keyword overlap rarely change the winning guide — every test case so far resolves to the same confidence (0.95) because the corpus is small and each category has exactly one dominant guide. That was a useful surprise: it means the current scoring formula is more brittle than it looks, and a larger or more overlapping corpus would likely need a real tie-breaker instead of just "highest score wins."

## AI Collaboration Reflection

I collaborated with OpenAI Codex while building this project. A helpful suggestion from Codex was to keep the AI layer local and deterministic so the project would stay reproducible and easy to grade. That made the final much easier to explain and verify.

One flawed suggestion was to rely on a standalone helper script rather than wiring the advice into the live booking flow. I corrected that by connecting the retrieval-backed guidance to the service pages and appointment dialog so the AI actually changes the user experience.

I also used Codex to help tighten the README, the architecture diagram, the evaluation notes, and the code comments so the repo reads like a polished portfolio project.

## Future Work

- Expand the retrieval corpus.
- Add semantic matching instead of simple keyword retrieval.
- Add more nuanced confidence scoring.
- Log user feedback on whether the advice was helpful.
