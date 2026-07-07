# AI Interactions Log

> **Note:** Most of this log documents AI collaboration on the original Module 2 build (the scheduling backend, before the final-project RAG extension) — it predates and does not cover the retrieval-advice layer (`ai_system.py`). The **Agentic Workflow Enhancement (Stretch)** section directly below is this final project's own work and *is* the submission for that stretch challenge.

## Agentic Workflow Enhancement (Stretch)

**What was built:** `ai_applied_agentic_loop.py` — a multi-step plan → act → check → revise loop, wired into every category booking form as a "🤖 Run Auto-Planner" button (see `bookings.py`'s `_render_agent_planner()`). This is deliberately different from `ai_system.py`'s `advise_service()` (a single retrieve-then-respond RAG call): the agent retrieves guidance, *then* proposes a concrete staff member and time slot, *then* checks that proposal against the pet's own existing schedule, and *revises* — trying the next slot or staff member — if a conflict is found, up to 3 attempts before giving up. The plan's staff/time choice becomes the actual default in the form's widgets, not just a suggestion printed alongside them. Every run appends its full reasoning trace to `logs/agent_traces.jsonl` (gitignored, like the rest of `logs/`, since it's a growing runtime log — so the traces below are embedded directly rather than linked).

**Why this design:** The slot search runs on fixed 15-minute increments rather than the task's own duration, so a proposed slot always lands on a value the form's Hour/Minute dropdowns can directly preselect. The first version of the escalation logic only checked each staff member's *single earliest* slot before moving to the next staff member — which failed in practice, because two staff members with no prior bookings both offer 07:00 first, so "try the next staff" just hit the identical conflict again. Verifying this dogfooding step directly, with a real conflicting pet task, is what caught it (see the two traces below): the fix was searching *every* open slot for a staff member before giving up on them, only escalating to the next staff member once a given staff truly has no conflict-free slot left.

**Trace 1 — same-staff slot search avoiding a pet conflict** (Bella already has a task at 07:00; the agent finds Maya Reyes's next open slot instead of giving up or double-booking):

```json
{"timestamp": "2026-07-07T03:47:38", "category": "grooming", "pet": "Bella", "success": true, "task_title": "Brush Coat", "staff_name": "Maya Reyes", "slot_start": "07:25", "slot_end": "07:50", "confidence": 0.95, "trace": [{"action": "plan", "detail": "Retrieved guidance for cat grooming: For grooming, start with the lowest-stress coat and hygiene tasks. Avoid piling on too many grooming tasks in one session. (confidence 0.95). Recommended task: Brush Coat."}, {"action": "act", "detail": "Attempt 1: proposed Maya Reyes at 07:25-07:50 — checked against Bella's existing schedule, no conflict found."}]}
```

**Trace 2 — cross-staff escalation when the first staff member is fully booked** (Priya Sharma has zero open slots all day; the agent rejects her entirely and succeeds with Diego Flores instead):

```json
{"timestamp": "2026-07-07T03:53:42", "category": "grooming", "pet": "Coco", "success": true, "task_title": "Brush Coat", "staff_name": "Diego Flores", "slot_start": "07:00", "slot_end": "07:15", "confidence": 0.95, "trace": [{"action": "plan", "detail": "Retrieved guidance for dog grooming: For grooming, start with the lowest-stress coat and hygiene tasks. Avoid piling on too many grooming tasks in one session. (confidence 0.95). Recommended task: Brush Coat."}, {"action": "check", "detail": "Attempt 1: Priya Sharma has no open slots today. Trying next staff member."}, {"action": "act", "detail": "Attempt 2: proposed Diego Flores at 07:00-07:15 — checked against Coco's existing schedule, no conflict found."}]}
```

**Verification performed:** unit-tested `plan_booking()` directly for all four paths (same-staff revision, cross-staff escalation, no-active-staff failure, no-task-options failure); confirmed via Streamlit's `AppTest` that clicking "Run Auto-Planner" on the real Grooming page pre-fills the actual staff-selectbox and hour/minute/period widgets (read back their live values, not just the displayed message) to match the plan; then submitted the form with those agent-picked defaults and confirmed a real booking was created. Full pytest suite (59 tests) still passes.

## AI Pre-Diagnostic Vet Assessment (Stretch)

**What was built:** `ai_applied_prediagnostic.py` plus a new "AI Pre-Diagnostic Assessment" page in the Veterinarian nav section. An owner picks a patient, checks off symptoms (or types free text), and the system retrieves a matching specialty from a dedicated corpus (`data/symptom_guides.csv`, one row per real clinic department) and recommends a specific active doctor in that department — checking the doctor's actual appointments today for an open slot, and escalating to the next matching doctor if the first is fully booked. This is a second, distinct RAG use case from `ai_system.py`'s service-task advice, plus a small check/revise escalation of its own (separate from `ai_applied_agentic_loop.py`'s staff/slot planner, since matching a *specialty* to a symptom and matching a *staff slot* to a pet's calendar are genuinely different decisions). Every assessment and recommendation appends a record to `logs/prediagnostic_traces.jsonl` (gitignored, like the other `logs/` files — traces embedded directly below).

**Why this design:** Symptom keywords are matched against `Doctor.department_name` — an existing controlled vocabulary already seeded for the clinic's doctor roster — rather than inventing a new specialty taxonomy that could drift out of sync with the real doctors. The one guardrail that had to be more than descriptive text is the emergency case: `ai_guides.csv`'s guardrail column is just explanatory text appended to a message, which isn't enough if an owner types something like "seizure" alongside an unrelated symptom that might otherwise score higher. So `EMERGENCY_KEYWORDS` in `ai_applied_prediagnostic.py` is checked first and unconditionally overrides the normal keyword-scoring match — the only guardrail in this project that's actual enforced code rather than descriptive text.

**Trace 1 — routine specialty match** (real clinic data; a limping dog correctly routes to Orthopedics):

```json
{"timestamp": "2026-07-07T05:26:15", "kind": "assessment", "symptom_text": "My dog is limping and wont put weight on his back leg, started 2 days ago after playing at the park", "department": "Orthopedics", "urgency": "routine", "confidence": 0.65}
{"timestamp": "2026-07-07T05:26:15", "kind": "recommendation", "department": "Orthopedics", "success": true, "doctor": "Dr. Levi Wilson", "slot_start": "07:00", "slot_end": "07:30", "trace": [{"action": "plan", "detail": "Matched department 'Orthopedics': 1 active doctor(s) available."}, {"action": "act", "detail": "Attempt 1: Dr. Levi Wilson has an opening at 07:00-07:30."}]}
```

**Trace 2 — emergency-keyword guardrail overriding the match** (real clinic data; "collapse" forces Emergency regardless of anything else):

```json
{"timestamp": "2026-07-07T05:26:28", "kind": "assessment", "symptom_text": "My cat suddenly collapsed and seems unresponsive", "department": "Emergency", "urgency": "emergency", "confidence": 0.95}
{"timestamp": "2026-07-07T05:26:28", "kind": "recommendation", "department": "Emergency", "success": true, "doctor": "Dr. Ethan Brown", "slot_start": "07:00", "slot_end": "07:30", "trace": [{"action": "plan", "detail": "Matched department 'Emergency': 1 active doctor(s) available."}, {"action": "act", "detail": "Attempt 1: Dr. Ethan Brown has an opening at 07:00-07:30."}]}
```

**Trace 3 — doctor escalation** (constructed fixture with two Dermatology doctors, since the real seeded roster has exactly one doctor per specialty; the first is fully booked all day, so the agent rejects him and succeeds with the second):

```json
{"timestamp": "2026-07-07T05:28:40", "kind": "assessment", "symptom_text": "constant itching and scratching for a week", "department": "Dermatology", "urgency": "routine", "confidence": 0.8}
{"timestamp": "2026-07-07T05:28:40", "kind": "recommendation", "department": "Dermatology", "success": true, "doctor": "Dr. Ivy Stone", "slot_start": "07:00", "slot_end": "07:30", "trace": [{"action": "plan", "detail": "Matched department 'Dermatology': 2 active doctor(s) available."}, {"action": "check", "detail": "Attempt 1: Dr. Lucas Garcia has no open slots today. Trying next candidate."}, {"action": "act", "detail": "Attempt 2: Dr. Ivy Stone has an opening at 07:00-07:30."}]}
```

**Trace 4 — unrecognized-symptom fallback** (no keyword in the corpus matches, so it falls back to General Practice with low confidence rather than guessing a specialty):

```json
{"timestamp": "2026-07-07T05:28:40", "kind": "assessment", "symptom_text": "acting a bit off but nothing specific I can point to", "department": "General Practice", "urgency": "routine", "confidence": 0.3}
{"timestamp": "2026-07-07T05:28:40", "kind": "recommendation", "department": "General Practice", "success": true, "doctor": "Dr. Ava Patel", "trace": [{"action": "plan", "detail": "Matched department 'General Practice': 1 active doctor(s) available."}, {"action": "act", "detail": "Attempt 1: Dr. Ava Patel has an opening at 07:00-07:30."}]}
```

**Verification performed:** unit-tested `assess_symptoms()`/`recommend_doctor()` directly for all four paths above; confirmed via Streamlit's `AppTest` that submitting the real assessment form renders the correct department/doctor recommendation and reasoning trace, and that emergency keywords render the red error banner; separately confirmed that `pages/appointments.py`'s booking dialog reads back the one-shot `st.session_state` prefill correctly — the doctor selectbox defaults to the recommended doctor's index and the reason text area is prefilled with the symptom description, then both keys are popped so a later, unrelated booking isn't affected. Full pytest suite (64 tests, 5 new) still passes.

## AI Medication Advisor (Stretch)

**What was built:** `ai_applied_medication_advisor.py` plus a new "AI Medication Advisor" page in the Veterinarian nav section. An owner enters a pet's already-diagnosed condition (from a common-conditions picker or free text), and the system retrieves a matching medication from a curated corpus (`data/medication_guides.csv`, ~38 real medications from [petmd.com/pet-medication](https://www.petmd.com/pet-medication)) — strictly the medication's real labeled indication, never a dose. This is a third distinct RAG use case in the project (alongside `ai_system.py`'s service-task advice and `ai_applied_prediagnostic.py`'s symptom-to-specialty triage), and it takes a firm diagnosis as input rather than raw symptoms or a service category.

**Why this design:** The user explicitly asked to go "strictly by the label," so every corpus entry is tagged with its real label status — `FDA-approved veterinary label` for drugs actually approved for animal use, or `Extra-label (human-labeled drug) used under veterinary direction` for the many commonly-used veterinary medications (e.g. famotidine, gabapentin-style drugs, trazodone) that are technically human-labeled and used off-label in practice. Pretending every entry was equally "on-label" would have been less accurate, not more. The corpus is a curated ~38-medication subset of the full ~200-item source list rather than an attempt at all of them — I was only confident I could state an accurate label indication for well-documented, commonly-prescribed medications; guessing at niche ones (e.g. Zycosan, Varenzin-CA1) risked stating something medically wrong dressed up as "the label." The one guardrail enforced in real code (not just descriptive text) is species safety: `recommend_medication()` filters candidates to the pet's species *before* scoring, as a hard filter — so a medication can never be suggested for a species its entry doesn't list, even if its keywords would otherwise score highest. This was verified directly: a species-mismatched query correctly returns no recommendation instead of guessing.

**Trace 1 — correct species-appropriate match** (a dog diagnosed with osteoarthritis correctly gets a dog-labeled NSAID):

```json
{"timestamp": "2026-07-07T06:47:49", "condition_text": "diagnosed with osteoarthritis, chronic joint pain, confirmed via x-ray", "species": "dog", "medication": "Carprofen (Rimadyl)", "label_status": "FDA-approved veterinary label", "confidence": 0.95}
```

**Trace 2 — species-safety guardrail blocking a mismatched suggestion** (the corpus's only hyperthyroidism entry, Methimazole, is cat-only; querying it for a dog correctly returns nothing rather than an unsafe guess):

```json
{"timestamp": "2026-07-07T06:47:49", "condition_text": "diagnosed with hyperthyroidism", "species": "dog", "medication": null, "label_status": null, "confidence": 0.0}
```

**Trace 3 — same condition, correct species** (the recommendation succeeds once the species actually matches the entry):

```json
{"timestamp": "2026-07-07T06:47:49", "condition_text": "diagnosed with hyperthyroidism, elevated T4", "species": "cat", "medication": "Methimazole", "label_status": "FDA-approved veterinary label", "confidence": 0.8}
```

**Verification performed:** unit-tested `recommend_medication()` directly for all five paths (species-appropriate match, species-blocked mismatch, a species entirely outside the corpus, correct-species success, and an unrecognized-condition fallback); confirmed via Streamlit's `AppTest` that selecting an actual dog patient with "Osteoarthritis / joint pain" correctly renders Carprofen with its real label text and guardrail. Full pytest suite (69 tests, 5 new) still passes.

## Adoption Match Quiz (Stretch)

**What was built:** `ai_applied_adoption_match.py` plus 4 new pages under a new "PawPal AI Pet Adoption" nav section: Breed Directory (filterable reference table + per-breed detail view), Adoption Match Quiz (4-question lifestyle quiz → top-5 ranked breed matches), Compare Breeds (side-by-side comparison), and My Adoption Plan (favorites, a pre-adoption checklist, and a timeline). This required authoring a new structured data module, `breed_traits.py` — energy level, grooming needs, shedding, hypoallergenic, apartment-friendly, kid-friendly, and beginner-friendly for all 117 seeded dog breeds and 61 seeded cat breeds — since no structured (as opposed to free-text) breed data existed anywhere in the repo before this.

**Why this design:** This is a fourth distinct RAG use case in the project, but the only one scoring structured quiz answers against structured breed data rather than free-text keywords. Each of the 4 quiz questions (energy level, grooming tolerance, apartment size, kid-friendliness) maps to exactly one `BreedTraits` axis, scored independently and summed to a score out of 4, then bucketed into a plain-language label (✅ Good match / ⚠️ Caution / ❌ Not ideal). Broader lifestyle concepts the user also wanted (hypoallergenic, beginner-friendly, low-shedding, active/calm, family-friendly) were deliberately kept as Breed Directory *filters* rather than additional quiz axes — they weren't part of the quiz's own 4 named questions, and folding them into the score would have silently changed what "the score" means. Health notes and temperament are reused from the existing `seed/seed_animals_distribution.py` risk data and `breed_personality.py`, not re-authored, to avoid two sources of truth. The mock "available now" adoption listings (`mock_shelter_listings.py`) are seeded deterministically off the breed name specifically so they don't jitter across reruns, and every place they render carries a fixed caption stating they're demo data — a small honesty guardrail so a viewer can't mistake fictional listings for the clinic's real patients.

**Trace — a full run of the quiz** (apartment-dweller wanting a calm, low-maintenance, kid-friendly dog):

```json
{"timestamp": "2026-07-07T09:55:21", "answers": {"species_preference": "dog", "energy_level": "low", "grooming_tolerance": "low", "apartment": true, "wants_kid_friendly": true}, "top_matches": [{"species": "dog", "breed": "Basset Hound", "score": 4, "label": "✅ Good match"}, {"species": "dog", "breed": "French Bulldog", "score": 4, "label": "✅ Good match"}, {"species": "dog", "breed": "Pug", "score": 4, "label": "✅ Good match"}, {"species": "dog", "breed": "American Hairless Terrier", "score": 3, "label": "✅ Good match"}, {"species": "dog", "breed": "American Staffordshire Terrier", "score": 3, "label": "✅ Good match"}]}
```

**Trace — a mismatch scoring lower** (same apartment/low-energy/kid-friendly answers scored directly against a Great Dane, via `score_breed()` rather than the ranked quiz):

```text
Great Dane: score 2/4, label "⚠️ Caution"
✗ Energy level is medium, you wanted low.
✓ Grooming needs (low) fit your tolerance.
✗ Not well suited to apartment living.
✓ Good with kids.
```

**Verification performed:** programmatic coverage check confirming `breed_traits.py` has zero missing/extra breeds against the seeded 117-dog/61-cat lists; unit-tested `score_breed()`/`best_matches()` directly for a full match, a partial mismatch, and species-preference filtering; confirmed via Streamlit's `AppTest` across all 4 adoption pages that the quiz form renders ranked results with correct labels, the Breed Directory's lifestyle filters and detail dialog work, and favoriting/comparing a breed on one page correctly appears on another (shared `st.session_state`). Full pytest suite (79 tests, 5 new) still passes.

## Agent Workflow

This project used two different AI coding assistants for two different jobs: Codex built the initial skeleton and backend, and Claude Code (used in the follow-up session covering this log) audited that work against the assignment, fixed what was actually broken, and completed the optional challenges. Codex was then brought back in for one narrow, specific job: acting as the second model in the Challenge 5 comparison below.

### Stage 1 — Initial build (Codex)

**What task did I give the agent?**

I asked Codex to help me complete the PawPal+ project from the CodePath instructions. The work was split into phases: create a UML design and class skeleton, implement the OOP backend, connect the backend to Streamlit, add scheduling algorithms, write pytest tests, and finish the README/reflection.

**What did the agent do?**

Codex created `pawpal_system.py` with the `Owner`, `Pet`, `Task`, and `Scheduler` classes, updated `diagrams/uml.mmd`, and added `diagrams/uml_final.mmd`. It implemented sorting by time, priority sorting, filtering, recurrence, conflict detection, and task completion. It also created `main.py` for CLI verification, rewrote `app.py` so Streamlit uses `st.session_state`, added `tests/test_pawpal.py`, and produced an initial pass at `README.md`/`reflection.md`.

### Stage 2 — Audit, bug fixes, and optional challenges (Claude Code)

**What task did I give the agent?**

I asked Claude Code to check whether Codex's finished project actually matched the assignment line by line, not just look complete, and to fix anything it found — including going after the optional challenges properly instead of leaving them undone or half-claimed.

**What did the agent do?**

- Audited every phase and all five optional challenges against the assignment text, and reported the gap honestly instead of assuming the project was done: the README's "Sample Output" section showed emoji formatting and two whole sections ("🚨 Next Urgent Task", "⭐ Today's Top 3 Priorities") that didn't exist anywhere in the actual code. It traced this to an abandoned git branch (`backup-current-ef1058f`) whose output had been pasted into the README on `main` without the code that produced it ever being merged.
- Fixed that by re-running `main.py` for real and replacing the fabricated output with the actual output, everywhere it appeared in the README.
- First made the emojis genuinely real instead of removing them: added `✅`/`⏳` status icons to `Task.summary()` and emoji section headers to `main.py`. On review this only satisfied Optional Challenge 4 loosely — the assignment lists three example formats (color-coded status, emojis for different task types, structured CLI tables) and only one was even partially covered, and not quite as literally described. Closed all three for real: (1) added `task_type_icon()` in `pawpal_system.py`, a keyword lookup that picks a different emoji per task category (🐕 walk, 💊 medication, 🍖 feeding, 🧼 grooming, 🏥 vet); (2) documented the color-coded `st.success()`/`st.warning()`/`st.info()` indicators already present in `app.py` from Phase 6, which Streamlit renders in distinct colors — that one just hadn't been credited before; (3) added the `tabulate` library (`requirements.txt`) and rewrote `main.py`'s `print_schedule()` to render every schedule section as a real table.
- Caught (from a screenshot the user shared of the README rendered in VS Code) that the first `tabulate` attempt used a Unicode box-drawing format (`tablefmt="rounded_outline"`) with the task-type icon in its own column with an empty header. In VS Code's markdown preview, emoji glyphs render wider than the single monospace column `tabulate` assumes, and that width error compounded across the row, breaking the box borders and clipping the "Status" header to "Stat". Fixed by merging the icon into the Task column's text instead of a dedicated icon-only column, and switching to `tablefmt="github"` (plain ASCII `|`/`-` characters, no Unicode corners) so any remaining width drift shows as minor uneven spacing instead of a visibly broken table.
- Swapped `tabulate` for `prettytable` at the user's request, keeping the same alignment fix in mind: used `PrettyTable` with `TableStyle.MARKDOWN` (pipe/dash characters, no box corners), not the library's default box-drawing style, which would have reintroduced the same fragility. Confirmed the emoji-in-Task-column output still renders cleanly with this style before adopting it. `requirements.txt` updated (`tabulate` removed, `prettytable>=3.10` added). Verified the new README output is byte-for-byte identical to a fresh `python main.py` run.
- Implemented `Scheduler.next_urgent_task()` and `Scheduler.top_priorities(n)` — a distinct ranking capability beyond the four base scheduling algorithms — which is what earns Optional Challenge 1.
- Implemented Optional Challenge 2 (JSON persistence) for real: `to_dict()`/`from_dict()` on `Task`, `Pet`, and `Owner`, plus `Owner.save_to_json()`/`Owner.load_from_json()`. Wired into `main.py` (a real save-then-reload round trip) and into `app.py` (auto-load on session start, auto-save after every render, so Streamlit state survives a full app restart, not just `st.session_state` within one session).
- Ran the Challenge 5 multi-model comparison below, and — this is the important part — didn't just record the comparison, but caught the integration gap in Codex's answer and fixed it in the actual codebase (see the Prompt Comparison section).
- Added 7 new pytest cases covering all of the above (13 total, up from 6), kept `diagrams/uml_final.mmd` in sync with every new/changed method signature, and verified everything by actually running `pytest`, running `main.py`, and booting the Streamlit app headlessly rather than assuming the code worked.

**What did I have to verify or fix manually?**

I reviewed each fix before accepting it — for example, confirming the "High Priority First" CLI section in the (formerly stale) README sample actually matched what `Scheduler.sort_by_priority_then_time()` produced, and checking that the new JSON persistence didn't silently break the existing recurrence/conflict tests before committing. I also kept the original conflict-detection design decision (exact date/time matches only, not overlapping durations) — that one was already a reasonable scope call from Stage 1 and didn't need to change.

---

## Prompt Comparison (Optional Challenge 5)

**Task:** the assignment's own suggested complex algorithmic task — rescheduling logic for weekly recurring tasks. Specifically: `Task.next_occurrence()` originally always computed `due_date + 7 days` for a weekly task, even if it was completed several days late, which could create a "next" task that was already overdue. I asked two different AI models the same self-contained prompt (the `Task`/`next_occurrence` code plus the question of how to fix this) to compare their solutions.

| | Model A: Codex | Model B: Claude |
|-|-----------------|------------------|
| **Model / tool used** | Codex (OpenAI coding agent) | Claude (Claude Code, this session) |
| **Prompt** | Same prompt given to both: the current `Task`/`next_occurrence()` code, plus "how would you implement rescheduling logic for a late-completed weekly task — anchor to the original due date or the completion date?" | Same prompt as Model A. |
| **Response summary** | Recommended a hybrid: keep the task anchored to its original cadence, but if completion is late, roll forward in `step` increments (`timedelta(weeks=1)`/`timedelta(days=1)`) past the completion date so the next occurrence always lands in the future. Provided a `next_occurrence(completed_on=...)` implementation using a `while` loop, and an updated `mark_task_complete()` signature. | Independently proposed the same core hybrid strategy (anchor to cadence, roll forward past late completions) before seeing Codex's code, since it's the standard pattern for recurring-reminder scheduling and avoids the schedule permanently drifting. Flagged two things Codex's answer didn't cover: (1) the fix is inert unless `Scheduler.mark_task_complete()` is also updated to pass `completed_on=date.today()` through to `next_occurrence()` — swapping in the new method alone changes nothing; (2) the `while` loop could be replaced with a closed-form `divmod` calculation, but for a pet-care app (nobody misses hundreds of weeks) the loop is clearer and just as correct, so not worth the complexity. |
| **What was useful** | A concrete, directly runnable implementation with a clear explanation of the anchoring tradeoff (original due date vs. completion date vs. hybrid). | Caught that the algorithm alone wasn't enough — the call site (`mark_task_complete`) had to change too, or the fix would silently do nothing. Confirmed the loop-based approach didn't need to be replaced with more "clever" math. |
| **What was flawed** | Didn't mention that the caller (`Scheduler.mark_task_complete()`) needed to be updated to actually pass a completion date — the sample code alone wouldn't change behavior if dropped in as-is. | No implementation-breaking flaw found; the main contribution was integration risk, not an alternative algorithm. |
| **Final decision** | Adopted Codex's `next_occurrence(completed_on)` implementation (the roll-forward-past-late-completions loop) largely as written. | Adopted Claude's fix for the integration gap: `Scheduler.mark_task_complete()` now accepts an optional `completed_on` and defaults it to `date.today()` before calling `next_occurrence()`, so the late-completion behavior actually takes effect without every caller having to remember to pass a date. |

**What changed in the codebase:** `Task.next_occurrence()` in `pawpal_system.py` now accepts `completed_on` and rolls the next date forward past it; `Scheduler.mark_task_complete()` passes `completed_on=completed_on or date.today()`. Covered by `test_weekly_recurrence_on_time_uses_original_cadence` and `test_weekly_recurrence_skips_ahead_when_completed_late` in `tests/test_pawpal.py`. `diagrams/uml_final.mmd` and the README's Smarter Scheduling table were updated to match.

---

## Additional Prompt Notes (single-tool, not the Challenge 5 submission)

From Stage 1 (the initial Codex build), I also compared two prompts given to the same tool (Codex) at different phases — useful for tracking how prompts evolved, but not a cross-model comparison, so it doesn't count toward Challenge 5 above.

| | Prompt A | Prompt B |
|-|----------|----------|
| **Model / tool used** | Codex, used for implementation planning | Codex, used for testing review |
| **Prompt** | "Build PawPal+ from the assignment phases and keep the backend separate from the UI." | "What should be tested for a pet scheduler with sorting, recurring tasks, and conflicts?" |
| **Response summary** | Suggested creating `Owner`, `Pet`, `Task`, and `Scheduler`, then wiring Streamlit to those classes through session state. | Suggested tests for completion, adding tasks, sorting, recurrence, filtering, and conflict detection. |
| **What was useful** | The phased approach kept the project from becoming one giant edit. | The test plan mapped directly to the assignment requirements. |
| **Problems noticed** | A more advanced conflict algorithm would have been possible but too large for the required scope. | Some edge cases, like overlapping durations, were noted but not implemented. |
| **Decision** | Keep a clean OOP design with simple exact-time conflict warnings. | Test the required behavior now and document future edge cases in the reflection. |

**Which approach did you use in your final implementation and why?**

I used the phased implementation approach because it matched the CodePath instructions and made each commit easier to understand. I also used the testing review to decide which behaviors were most important to verify before submitting. I rejected extra complexity when it would make the project harder to explain, especially around calendar-style overlap detection.
