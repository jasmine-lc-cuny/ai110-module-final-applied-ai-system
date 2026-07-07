# PawPal+ Applied AI System

PawPal+ is the base project for this final applied-AI system. The original Module 2 app was a Streamlit pet-care planner that let an owner manage pets, schedule tasks, detect conflicts, and track recurring routines. This final version extends PawPal with a local retrieval-augmented guidance layer so the booking flow can suggest smarter service choices and explain why those choices make sense.

## Summary

PawPal+ helps a pet owner schedule grooming, sitting, training, walking, dog cafe, and veterinary bookings. The applied AI feature retrieves guidance from a local corpus before suggesting tasks, adds a confidence score, writes a JSONL log of each advice run, and keeps the user inside a safe guardrailed flow instead of making the app guess blindly.

## Original Project

The original project from Module 2 was a pet-care scheduling app. It stored pets and tasks, supported recurrence, showed today's schedule, and surfaced conflicts. This final keeps that foundation, but adds retrieval-backed guidance and explanation so the system behaves more like an applied AI assistant.

## Architecture

The system architecture source is stored in `diagrams/architecture.mmd`.

## What It Does

- Retrieves care guidance before suggesting a booking choice.
- Preselects more helpful task defaults on service pages.
- Shows AI suggestions in the booking and appointment flows.
- Logs each advice run to `logs/ai_advice.jsonl`.
- Runs a multi-step agentic planner ("🤖 Run Auto-Planner") on each booking form that retrieves guidance, proposes a staff member and time slot, checks its own proposal against the pet's existing schedule, and revises if there's a conflict — logging the full reasoning trace to `logs/agent_traces.jsonl`.
- Keeps the original scheduling, conflict, and recurrence logic intact.
- Uses the existing Streamlit app as the main user experience.

## AI Feature Mapping

The assignment's example extension combos, mapped to what's actually implemented in this repo:

| Extension Combo | Status | Files |
|---|---|---|
| RAG + testing + guardrails | ✅ Implemented (required feature) | `ai_system.py` (retrieval + guardrail text), `evaluate_ai.py` (reliability harness), `tests/test_pawpal.py` (AI-specific tests) |
| Agentic loop + logging | ✅ Implemented (stretch) | `ai_applied_agentic_loop.py` (plan → act → check → revise loop), `logs/agent_traces.jsonl` (reasoning trace log), traces also embedded in `ai_interactions.md` |
| RAG + validation | 🟡 Partial | `ai_system.py` matches guidance by species/category before returning it, but there's no separate, explicit validation/scoring pass reported back to the user beyond the confidence score |
| RAG + guardrails + check/revise (stretch) | ✅ Implemented (stretch) | `ai_applied_prediagnostic.py` (symptom → specialty retrieval, a hardcoded emergency-keyword guardrail that's actual enforced code, and a doctor-availability check/revise escalation), `pages/ai_prediagnostic_assessment.py`, `logs/prediagnostic_traces.jsonl` |
| RAG + guardrails (stretch) | ✅ Implemented (stretch) | `ai_applied_medication_advisor.py` (diagnosed condition → curated medication retrieval, with a hard species-safety filter enforced in code, not just a scoring bonus), `pages/ai_medication_advisor.py`, `logs/medication_advice.jsonl` |
| RAG + ranking (stretch) | ✅ Implemented (stretch) | `ai_applied_adoption_match.py` (lifestyle quiz answers scored against every seeded breed's structured traits, ranked top-5 with a Good match/Caution/Not ideal label and a per-axis reasoning trace), `pages/adoption_quiz.py`, `logs/adoption_match_traces.jsonl` |

## Setup

```bash
pip install -r requirements.txt
```

Run the CLI demo:

```bash
python main.py
```

Run the Streamlit app:

```bash
python -m streamlit run app.py
```

Run tests:

```bash
python -m pytest
```

Run the AI evaluation script:

```bash
python evaluate_ai.py
```

## Sample Interactions

Example 1:

```text
Goal: Schedule grooming for Bella, my cat.
AI suggestion: For grooming, start with the lowest-stress coat and hygiene tasks. Avoid piling on too many grooming tasks in one session.
Result: Brush Coat, Wash / Bath, Trim Nails
```

Example 2:

```text
Goal: Book a veterinary visit for Mochi, my dog.
AI suggestion: For veterinary visits, choose the medical task that matches the concern. Always use the owner-provided reason and avoid inventing treatment details.
Result: Vet Appointment with a doctor assigned
```

Example 3:

```text
Goal: Add dog cafe meals for a dog.
AI suggestion: For the Dog Cafe section, meal choices are the main action. Keep cafe bookings to one meal slot.
Result: Breakfast, Lunch, Dinner
```

## Agentic Booking Planner (Stretch: Agentic Workflow Enhancement)

Every category booking form has a "🤖 Run Auto-Planner" button. Unlike `advise_service()` (a single retrieve-then-respond RAG call), this runs a multi-step loop: retrieve care guidance → propose a staff member and time slot → check that slot against the pet's own existing schedule → if it conflicts, revise by trying the next slot or staff member — up to 3 attempts before giving up. The plan's staff/time choice becomes the actual default in the booking form's widgets (not just displayed text), and the full reasoning trace is logged to `logs/agent_traces.jsonl`. Full traces with intermediate reasoning steps are in `ai_interactions.md`.

Real example (pet has a conflicting task at the first staff member's earliest slot):

```text
Goal: Auto-plan a grooming booking for Bella, my cat.

[plan] Retrieved guidance for cat grooming: For grooming, start with the
       lowest-stress coat and hygiene tasks. Avoid piling on too many
       grooming tasks in one session. (confidence 0.95). Recommended
       task: Brush Coat.
[act]  Attempt 1: proposed Maya Reyes at 07:25-07:50 — checked against
       Bella's existing schedule, no conflict found.

Result: Brush Coat with Maya Reyes at 7:25 AM (skipped 7:00 AM, which
        was already booked on Bella's schedule).
```

## AI Pre-Diagnostic Vet Assessment (Stretch: RAG + Guardrails)

A new "AI Pre-Diagnostic Assessment" page in the Veterinarian section lets an owner answer a short symptom questionnaire (checklist + free text + when it started), then `ai_applied_prediagnostic.py` retrieves a matching specialty from a second, dedicated corpus (`data/symptom_guides.csv`) and recommends a specific active doctor whose `department_name` matches, checking that doctor's real appointments for an open slot today and escalating to the next matching doctor if they're fully booked. Unlike the existing guardrail text in `ai_guides.csv` (descriptive only), this feature has one actual code-enforced guardrail: a hardcoded `EMERGENCY_KEYWORDS` check that overrides the retrieval match entirely — typing "seizure" or "collapse" always routes to Emergency/urgent care regardless of anything else in the text. The recommendation hands off to the existing Appointments booking dialog via a one-shot `st.session_state` prefill (doctor + reason), so the owner doesn't have to re-type anything.

Real example (routine match):

```text
Goal: Assess a dog that's limping and won't put weight on a back leg.

Suggested specialty: Orthopedics (confidence 0.65)
Limping and joint stiffness are usually orthopedic in nature. Avoid strenuous
activity until a vet has evaluated the leg or joint.

[plan] Matched department 'Orthopedics': 1 active doctor(s) available.
[act]  Attempt 1: Dr. Levi Wilson has an opening at 07:00-07:30.

Result: Recommended Dr. Levi Wilson at 07:00.
```

Real example (emergency-keyword guardrail overriding the match):

```text
Goal: Assess a cat that suddenly collapsed and is unresponsive.

🚨 'collapse' indicates a potential emergency. Do not wait for a scheduled
   appointment; contact an emergency vet immediately.
Suggested specialty: Emergency (confidence 0.95)

[plan] Matched department 'Emergency': 1 active doctor(s) available.
[act]  Attempt 1: Dr. Ethan Brown has an opening at 07:00-07:30.
```

Each assessment and recommendation appends a record to `logs/prediagnostic_traces.jsonl`; the actual lines written by the two runs above:

```json
{"timestamp": "2026-07-07T05:26:15", "kind": "assessment", "symptom_text": "My dog is limping and wont put weight on his back leg, started 2 days ago after playing at the park", "department": "Orthopedics", "urgency": "routine", "confidence": 0.65}
{"timestamp": "2026-07-07T05:26:15", "kind": "recommendation", "department": "Orthopedics", "success": true, "doctor": "Dr. Levi Wilson", "slot_start": "07:00", "slot_end": "07:30", "trace": [{"action": "plan", "detail": "Matched department 'Orthopedics': 1 active doctor(s) available."}, {"action": "act", "detail": "Attempt 1: Dr. Levi Wilson has an opening at 07:00-07:30."}]}
{"timestamp": "2026-07-07T05:26:28", "kind": "assessment", "symptom_text": "My cat suddenly collapsed and seems unresponsive", "department": "Emergency", "urgency": "emergency", "confidence": 0.95}
{"timestamp": "2026-07-07T05:26:28", "kind": "recommendation", "department": "Emergency", "success": true, "doctor": "Dr. Ethan Brown", "slot_start": "07:00", "slot_end": "07:30", "trace": [{"action": "plan", "detail": "Matched department 'Emergency': 1 active doctor(s) available."}, {"action": "act", "detail": "Attempt 1: Dr. Ethan Brown has an opening at 07:00-07:30."}]}
```

## AI Medication Advisor (Stretch: RAG + Guardrails)

A new "AI Medication Advisor" page in the Veterinarian section lets an owner enter a pet's already-diagnosed condition (from a common-conditions picker or free text), and `ai_applied_medication_advisor.py` retrieves a matching medication from a curated, ~38-entry corpus (`data/medication_guides.csv`) built from [petmd.com/pet-medication](https://www.petmd.com/pet-medication)'s real label indications — never a dose, and strictly from that medication's actual labeled use. Every entry is also tagged with its true label status, since not every commonly-used veterinary drug is actually FDA-approved for animals: entries are marked either `FDA-approved veterinary label` or `Extra-label (human-labeled drug) used under veterinary direction` (e.g. Gabapentin-style human drugs used off-label in practice), so the recommendation is honest about what "the label" actually says. The one guardrail enforced in real code here is species safety: a medication is filtered out of the candidate pool entirely if its entry doesn't list the pet's species — a hard filter, not just a scoring bonus — so a cat can never be recommended a dog-only NSAID (or vice versa) even if its keywords would otherwise score highest.

Real example (correct species-appropriate match):

```text
Goal: Recommend a medication for a dog diagnosed with osteoarthritis.

Recommended medication: Carprofen (Rimadyl) (confidence 0.95)
Label status: FDA-approved veterinary label
Carprofen (Rimadyl) is labeled for control of pain and inflammation
associated with osteoarthritis and for control of postoperative pain
following soft tissue and orthopedic surgery in dogs.
⚠️ NSAID: do not combine with other NSAIDs or steroids; requires baseline
   bloodwork and periodic monitoring; confirm dosing and suitability with
   your veterinarian.
```

Real example (species-safety guardrail blocking a mismatched suggestion):

```text
Goal: Recommend a medication for a dog diagnosed with hyperthyroidism.
(Methimazole is the corpus's only hyperthyroidism entry, but it's cat-only.)

Result: No medication in this curated corpus matches that condition. This
is a small, curated reference, not a full formulary — consult your
veterinarian.

Goal: Same condition, correct species (cat).
Recommended medication: Methimazole (confidence 0.80)
Label status: FDA-approved veterinary label
Methimazole is labeled for the treatment of hyperthyroidism in cats.
```

Each recommendation appends a record to `logs/medication_advice.jsonl`; the actual lines written by the three runs above:

```json
{"timestamp": "2026-07-07T06:47:49", "condition_text": "diagnosed with osteoarthritis, chronic joint pain, confirmed via x-ray", "species": "dog", "medication": "Carprofen (Rimadyl)", "label_status": "FDA-approved veterinary label", "confidence": 0.95}
{"timestamp": "2026-07-07T06:47:49", "condition_text": "diagnosed with hyperthyroidism", "species": "dog", "medication": null, "label_status": null, "confidence": 0.0}
{"timestamp": "2026-07-07T06:47:49", "condition_text": "diagnosed with hyperthyroidism, elevated T4", "species": "cat", "medication": "Methimazole", "label_status": "FDA-approved veterinary label", "confidence": 0.8}
```

## Adoption Match Quiz (Stretch: RAG + Ranking)

The "PawPal AI Pet Adoption" nav section's Adoption Match Quiz page asks 4 lifestyle questions (desired energy level, grooming tolerance, apartment vs. yard, and whether the pet must be kid-friendly), and `ai_applied_adoption_match.py` scores every one of the 178 seeded breeds against the answers using `breed_traits.py`'s structured per-breed data (energy, grooming needs, shedding, hypoallergenic, apartment-friendly, kid-friendly, beginner-friendly — hand-authored for all 117 dog and 61 cat breeds, alongside the existing `breed_personality.py` temperament sentences and `seed/seed_animals_distribution.py`'s health-risk data, which are reused rather than duplicated). Each breed gets a score out of 4 equally-weighted axes, a plain-language "✅ Good match / ⚠️ Caution / ❌ Not ideal" label, and a per-axis reasoning trace explaining exactly which preferences matched or didn't — the same retrieval-and-rank shape as `ai_system.py`/`ai_applied_prediagnostic.py`, applied to structured quiz answers instead of free-text keywords.

Real example:

```text
Quiz answers: species=dog, energy=low, grooming tolerance=low, apartment=yes, kids=yes

1. Basset Hound — ✅ Good match (4/4)
   ✓ Energy level matches (low).
   ✓ Grooming needs (low) fit your tolerance.
   ✓ Fits an apartment/small space.
   ✓ Good with kids.
2. French Bulldog — ✅ Good match (4/4)
3. Pug — ✅ Good match (4/4)
4. American Hairless Terrier — ✅ Good match (3/4)
   ✗ Energy level is high, you wanted low.
5. American Staffordshire Terrier — ✅ Good match (3/4)
```

Real embedded trace from `logs/adoption_match_traces.jsonl`:

```json
{"timestamp": "2026-07-07T09:55:21", "answers": {"species_preference": "dog", "energy_level": "low", "grooming_tolerance": "low", "apartment": true, "wants_kid_friendly": true}, "top_matches": [{"species": "dog", "breed": "Basset Hound", "score": 4, "label": "✅ Good match"}, {"species": "dog", "breed": "French Bulldog", "score": 4, "label": "✅ Good match"}, {"species": "dog", "breed": "Pug", "score": 4, "label": "✅ Good match"}, {"species": "dog", "breed": "American Hairless Terrier", "score": 3, "label": "✅ Good match"}, {"species": "dog", "breed": "American Staffordshire Terrier", "score": 3, "label": "✅ Good match"}]}
```

The Breed Directory, Compare Breeds, and My Adoption Plan pages round out the section: lifestyle filters and a per-breed detail view (temperament, exercise needs, grooming/health notes) on Breed Directory, a side-by-side comparison on Compare Breeds, and session-scoped favorites, a pre-adoption checklist, and a before/first-week/first-month timeline on My Adoption Plan. All three reuse the same `breed_traits.py`/`breed_personality.py` data as the quiz rather than maintaining separate copies.

## Reproducible Execution Evidence

All output below is pasted directly from real runs on 2026-07-06, not hand-written. Reproduce it yourself with `pip install -r requirements.txt` followed by the commands shown.

### End-to-end system run (`python main.py`)

The CLI demo builds two pets with four tasks, then exercises the full scheduling engine: sorting, priority ranking, conflict detection, recurrence, and JSON persistence.

```text
PawPal+ schedule for Jordan
================================
📅 Today's Schedule

| Time     | Pet        | Species | Task                    | Duration | Priority  | Frequency | Due Date   | Status  |
| :--------| :----------| :-------| :-----------------------| :--------| :---------| :---------| :----------| :-------|
| 7:30 AM  | 🐱🐈 Luna  | cat     | 🍖 Breakfast            | 10 min   | 🔴 high   | daily     | 2026-07-06 | ⏳ open |
| 8:00 AM  | 🐶🐕 Mochi | dog     | 🐕 Morning walk         | 30 min   | 🔴 high   | daily     | 2026-07-06 | ⏳ open |
| 8:00 AM  | 🐱🐈 Luna  | cat     | 🪮 Brush coat           | 15 min   | 🟡 medium | once      | 2026-07-06 | ⏳ open |
| 12:00 PM | 🐶🐕 Mochi | dog     | 💊 Heartworm medication | 5 min    | 🔴 high   | once      | 2026-07-06 | ⏳ open |

⚠️ Conflict Warnings

  Conflict on 2026-07-06 at 8:00 AM: Mochi: Morning walk, Luna: Brush coat

🔁 Recurring Task Created

| Time    | Pet        | Species | Task            | Duration | Priority | Frequency | Due Date   | Status  |
| :-------| :----------| :-------| :---------------| :--------| :--------| :---------| :----------| :-------|
| 8:00 AM | 🐶🐕 Mochi | dog     | 🐕 Morning walk | 30 min   | 🔴 high  | daily     | 2026-07-07 | ⏳ open |

💾 Saved to main_demo_data.json and reloaded a fresh Owner from disk
Reloaded Schedule (from main_demo_data.json)

| Time     | Pet        | Species | Task                    | Duration | Priority  | Frequency | Due Date   | Status  |
| :--------| :----------| :-------| :-----------------------| :--------| :---------| :---------| :----------| :-------|
| 7:30 AM  | 🐱🐈 Luna  | cat     | 🍖 Breakfast            | 10 min   | 🔴 high   | daily     | 2026-07-06 | ⏳ open |
| 8:00 AM  | 🐱🐈 Luna  | cat     | 🪮 Brush coat           | 15 min   | 🟡 medium | once      | 2026-07-06 | ⏳ open |
| 12:00 PM | 🐶🐕 Mochi | dog     | 💊 Heartworm medication | 5 min    | 🔴 high   | once      | 2026-07-06 | ⏳ open |
```

(Full output includes additional sections — priority ranking, per-pet filtering, next-urgent-task, and top-3-priorities tables — omitted here for length; run the command yourself to see them all.)

### AI feature behavior (retrieval-backed advice)

```text
>>> advise_service("grooming", "cat", ['Brush Coat', 'Wash / Bath', 'Hair Cut', 'Trim Nails', 'Ear Cleaning', 'Teeth Brushing'])
Recommended: ('Brush Coat', 'Wash / Bath', 'Trim Nails')
Confidence: 0.95
Explanation: For grooming, start with the lowest-stress coat and hygiene tasks. Avoid piling on too many grooming tasks in one session.

>>> advise_service("veterinary", "dog", ['Vet Appointment', 'Give Medication', 'Injection Medication', 'Other (custom)'])
Recommended: ('Vet Appointment', 'Give Medication', 'Injection Medication')
Confidence: 0.95
Explanation: For veterinary visits, choose the medical task that matches the concern. Always use the owner-provided reason and avoid inventing treatment details.

>>> advise_service("special_services", "dog", ['Breakfast', 'Lunch', 'Dinner'])
Recommended: ('Breakfast', 'Lunch', 'Dinner')
Confidence: 0.95
Explanation: For the Dog Cafe section, meal choices are the main action. Keep cafe bookings to one meal slot.
```

Each of these calls also appends a record to `logs/ai_advice.jsonl`. The actual lines written by the run above:

```json
{"timestamp": "2026-07-06T17:47:28", "category": "grooming", "species": "cat", "matched_category": "grooming", "matched_species": "all", "confidence": 0.95}
{"timestamp": "2026-07-06T17:47:28", "category": "veterinary", "species": "dog", "matched_category": "veterinary", "matched_species": "all", "confidence": 0.95}
{"timestamp": "2026-07-06T17:47:28", "category": "special_services", "species": "dog", "matched_category": "special_services", "matched_species": "dog", "confidence": 0.95}
```

### Agentic planner behavior (`plan_booking()`)

Two real runs of `ai_applied_agentic_loop.plan_booking()` — the second one shows the agent rejecting a fully-booked staff member and escalating to the next one:

```text
>>> plan_booking(category="grooming", pet=Bella (cat), title_options=[...], active_staff=[Maya Reyes], ...)
success: True | staff: Maya Reyes | slot: 07:25-07:50
  [plan] Retrieved guidance for cat grooming: For grooming, start with the lowest-stress coat and hygiene
         tasks. Avoid piling on too many grooming tasks in one session. (confidence 0.95). Recommended
         task: Brush Coat.
  [act] Attempt 1: proposed Maya Reyes at 07:25-07:50 — checked against Bella's existing schedule, no
        conflict found.

>>> plan_booking(category="grooming", pet=Coco (dog), title_options=[...], active_staff=[Priya Sharma (fully booked), Diego Flores], ...)
success: True | staff: Diego Flores | slot: 07:00-07:15
  [plan] Retrieved guidance for dog grooming: For grooming, start with the lowest-stress coat and hygiene
         tasks. Avoid piling on too many grooming tasks in one session. (confidence 0.95). Recommended
         task: Brush Coat.
  [check] Attempt 1: Priya Sharma has no open slots today. Trying next staff member.
  [act] Attempt 2: proposed Diego Flores at 07:00-07:15 — checked against Coco's existing schedule, no
        conflict found.
```

Each run appends a record to `logs/agent_traces.jsonl`, e.g. the second run above:

```json
{"timestamp": "2026-07-07T03:53:42", "category": "grooming", "pet": "Coco", "success": true, "task_title": "Brush Coat", "staff_name": "Diego Flores", "slot_start": "07:00", "slot_end": "07:15", "confidence": 0.95, "trace": [{"action": "plan", "detail": "Retrieved guidance for dog grooming: For grooming, start with the lowest-stress coat and hygiene tasks. Avoid piling on too many grooming tasks in one session. (confidence 0.95). Recommended task: Brush Coat."}, {"action": "check", "detail": "Attempt 1: Priya Sharma has no open slots today. Trying next staff member."}, {"action": "act", "detail": "Attempt 2: proposed Diego Flores at 07:00-07:15 — checked against Coco's existing schedule, no conflict found."}]}
```

### Reliability / guardrail results (`python evaluate_ai.py`)

```text
Applied AI Evaluation
=====================
This harness checks the local advice layer and its integration points.
Retrieval guides loaded: 6
PASS: Retrieval corpus available
PASS: Advice layer returned grooming guidance with confidence 0.95
PASS: Suggested defaults -> Brush Coat, Wash / Bath, Trim Nails
PASS: Pre-diagnostic assessment matched Emergency guardrail and Dermatology retrieval correctly
PASS: Medication advisor matched osteoarthritis retrieval and blocked a species-inappropriate suggestion
```

### Automated test suite (`python -m pytest -q`)

```text
........................................................................ [ 97%]
..                                                                       [100%]
74 passed in 0.09s
```

74/74 tests pass, including two dedicated to the AI advice layer (`test_ai_advice_prefers_grooming_defaults_for_cats`, `test_ai_advice_prefers_veterinary_defaults_for_dogs`), five dedicated to the pre-diagnostic assessment (`test_prediagnostic_matches_dermatology_for_itching`, `test_prediagnostic_forces_emergency_for_emergency_keyword`, `test_prediagnostic_falls_back_to_general_practice_for_unrecognized_text`, `test_recommend_doctor_escalates_when_first_match_is_fully_booked`, `test_recommend_doctor_falls_back_to_general_practice_when_no_specialist_available`), five dedicated to the medication advisor (`test_medication_advisor_matches_osteoarthritis_for_dog`, `test_medication_advisor_never_recommends_species_inappropriate_drug`, `test_medication_advisor_blocks_species_outside_the_corpus`, `test_medication_advisor_matches_hyperthyroidism_for_cat`, `test_medication_advisor_falls_back_when_no_condition_matches`), and five dedicated to realistic grooming durations (`test_dog_size_tier_prefers_breed_over_weight`, `test_dog_size_tier_falls_back_to_weight_for_unknown_breed`, `test_dog_size_tier_defaults_to_medium_with_no_breed_or_weight`, `test_grooming_duration_scales_with_dog_size`, `test_grooming_duration_for_cats_is_a_short_flat_range`), alongside the original PawPal scheduling suite.

## Reliability and Evaluation

The project includes automated tests plus a simple evaluation script for the advice layer. The evaluation script checks that the retrieval corpus is available and that the advice flow is wired into the app behavior. The existing PawPal scheduling tests still cover task completion, recurrence, sorting, conflict detection, persistence, and the new AI advice helpers.

## Design Decisions

- I kept the base PawPal scheduling engine instead of rebuilding everything from scratch.
- I used a small local retrieval corpus so the project is reproducible and easy to explain.
- I made the AI advice visible in the real booking flow rather than only in a standalone script.
- I kept the system deterministic so reviewers can rerun it and get the same structure every time.
- The agentic planner searches in fixed 15-minute increments (not the task's own duration) so a proposed slot always lands on a value the booking form's Hour/Minute dropdowns can directly preselect — trading a little precision for a plan that's actually usable as a form default, not just a suggestion the user has to re-enter by hand.
- The planner caps itself at 3 staff attempts (`MAX_ATTEMPTS`) rather than searching every staff member indefinitely, so it fails fast and reports why instead of silently hanging on a fully-booked section.
- The pre-diagnostic assessment matches symptom keywords against `Doctor.department_name` (an existing, already-seeded controlled vocabulary of specialties) rather than introducing a new taxonomy to keep in sync — retrieval and the real doctor roster can never drift apart.
- The emergency-keyword check is real, hardcoded, always-checked-first code (`EMERGENCY_KEYWORDS` in `ai_applied_prediagnostic.py`), not just descriptive guardrail text in a CSV — a deliberate choice so a genuinely dangerous symptom can't be silently outscored by an unrelated keyword match.
- The medication advisor's corpus is a curated ~38-medication subset of the full petmd.com list, not all ~200 — every entry needed a label indication I could verify with confidence, and a smaller, defensible corpus beats a larger one with guessed entries for obscure drugs.
- The medication advisor never states a dose, only the medication and its real labeled condition — dosing depends on weight, species, and other medications, which is squarely a licensed veterinarian's call, not this project's.
- Species is a hard filter in the medication advisor, applied before scoring, not a bonus added to the score — so a medication can never be suggested for a species its entry doesn't list, even if its keywords would otherwise win.
- Grooming durations are realistic instead of one flat number: `grooming_duration.py` sizes a dog's visit by breed (falling back to weight, then to "medium" if neither is known) and gives cats a shorter flat range, based on typical full-service grooming times. The seeder schedules each pet's one monthly grooming visit back-to-back into an actual groomer's day, capped at business hours, rather than giving every pet a same-length appointment every single day regardless of size.
- Each medication entry is tagged with its real label status (`FDA-approved veterinary label` vs `Extra-label (human-labeled drug) used under veterinary direction`) rather than presenting every entry as equally "labeled" — several commonly-used veterinary drugs (e.g. gabapentin-style human drugs) are legitimately off-label in animals, and a "strictly by the label" feature should say so.
- The adoption quiz's 4 scoring axes map 1:1 onto the 4 questions actually asked (energy, grooming, apartment fit, kid-friendliness); broader lifestyle concepts the user also wanted (hypoallergenic, beginner-friendly, low-shedding, active/calm, family-friendly) live as Breed Directory filters instead of quiz axes, since they weren't part of the quiz's own question set and folding them in would silently change what the score means.
- Every mock "available now" adoption listing is generated deterministically from the breed name (not the process RNG), so a given breed shows the same fictional listing across reruns instead of jittering — and every place they render shows a fixed caption stating they're demo data, not real shelter inventory, so a demo viewer can't mistake them for the clinic's actual patients.
- Favorites, the compare-breeds selection, and the adoption checklist are session-only (`st.session_state`), not saved to `data.json` — adoption browsing isn't tied to an existing clinic `Owner` record, so there's no natural place on disk for this state to live, and every other page-local UI toggle in the app already follows this session-only pattern.

## Testing Summary

- PawPal scheduling tests still validate the backend behavior.
- `evaluate_ai.py` provides a lightweight reliability check for the applied-AI layer.
- The app launches cleanly through Streamlit and the AI advice appears on service and appointment pages.
- The agentic planner was verified with real (not fabricated) runs covering: a successful same-staff slot search that skips a conflicting time, a cross-staff escalation when the first staff member is fully booked, and both failure paths (no active staff, no task options) — see `ai_interactions.md` for the full traces. Also verified end-to-end via Streamlit's `AppTest`: clicking "Run Auto-Planner" pre-fills the real staff/time widgets (not just displayed text), and submitting the form with those defaults creates the booking successfully.
- The pre-diagnostic assessment was verified with real (not fabricated) runs covering: a routine specialty match (Orthopedics), the emergency-keyword guardrail overriding the match (Emergency), an unrecognized-symptom fallback (General Practice), and a doctor-escalation when the first matching doctor's day is fully booked — see `ai_interactions.md` for the full traces. Also verified end-to-end via Streamlit's `AppTest`: submitting the symptom form renders the correct recommendation and emergency banner, and the Appointments booking dialog correctly reads back the one-shot `st.session_state` prefill (doctor selectbox defaults to the recommended doctor, reason defaults to the symptom text) and clears it after use.
- The medication advisor was verified with real (not fabricated) runs covering: a correct species-appropriate match (Carprofen for a dog with osteoarthritis), the species-safety filter blocking a mismatched suggestion (a dog can't get the cat-only hyperthyroidism drug), a species outside the corpus entirely returning no recommendation instead of a guess, and the correct match once species is corrected (Methimazole for a cat) — see `ai_interactions.md` for the full traces. Also verified end-to-end via Streamlit's `AppTest`: selecting a real dog patient and "Osteoarthritis / joint pain" correctly returned Carprofen.
- Grooming's realistic durations were verified directly against the regenerated demo data: all 170 dog/cat patients get exactly one grooming visit spread across the month (5-6 per day, not clustered), durations genuinely vary by pet (e.g. a Golden Retriever's 157 minutes vs. a cat's 31 minutes in one real run), and no groomer's appointments overlap. Also verified via `AppTest` that the manual booking form's duration default itself changes per selected pet instead of a flat number.
- `breed_traits.py`'s coverage was verified programmatically (zero missing/extra breeds against the seeded 117 dog / 61 cat lists) before any page used it. The adoption match quiz was verified with real (not fabricated) runs covering: a full 4/4 match, a partial match where one axis fails (apartment-unfriendly breed scored down and labeled "Caution"), and species-preference filtering restricting results to only dogs or only cats — see `logs/adoption_match_traces.jsonl` for real traces. Also verified end-to-end via `AppTest` across all 4 adoption pages: submitting the quiz renders ranked results with correct labels, the Breed Directory's lifestyle filters and detail view render correctly, favoriting/comparing a breed on one page correctly shows up on My Adoption Plan / Compare Breeds (session state shared across pages), and the breed detail dialog opens with correct content.

## Notes

Responsible-AI reflection and collaboration details live in `model_card.md`.
