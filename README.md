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
- Keeps the original scheduling, conflict, and recurrence logic intact.
- Uses the existing Streamlit app as the main user experience.

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

### Reliability / guardrail results (`python evaluate_ai.py`)

```text
Applied AI Evaluation
=====================
This harness checks the local advice layer and its integration points.
Retrieval guides loaded: 6
PASS: Retrieval corpus available
PASS: Advice layer returned grooming guidance with confidence 0.95
PASS: Suggested defaults -> Brush Coat, Wash / Bath, Trim Nails
```

### Automated test suite (`python -m pytest -q`)

```text
...........................................................              [100%]
59 passed in 0.04s
```

59/59 tests pass, including two dedicated to the AI advice layer (`test_ai_advice_prefers_grooming_defaults_for_cats`, `test_ai_advice_prefers_veterinary_defaults_for_dogs`) alongside the original PawPal scheduling suite.

## Reliability and Evaluation

The project includes automated tests plus a simple evaluation script for the advice layer. The evaluation script checks that the retrieval corpus is available and that the advice flow is wired into the app behavior. The existing PawPal scheduling tests still cover task completion, recurrence, sorting, conflict detection, persistence, and the new AI advice helpers.

## Design Decisions

- I kept the base PawPal scheduling engine instead of rebuilding everything from scratch.
- I used a small local retrieval corpus so the project is reproducible and easy to explain.
- I made the AI advice visible in the real booking flow rather than only in a standalone script.
- I kept the system deterministic so reviewers can rerun it and get the same structure every time.

## Testing Summary

- PawPal scheduling tests still validate the backend behavior.
- `evaluate_ai.py` provides a lightweight reliability check for the applied-AI layer.
- The app launches cleanly through Streamlit and the AI advice appears on service and appointment pages.

## Notes

Responsible-AI reflection and collaboration details live in `model_card.md`.
