"""Shared state and UI helpers used across every page of the multi-page app."""

from pathlib import Path

import streamlit as st

from pawpal_system import Owner, Scheduler, Task, format_time_12h, pet_species_icon, task_type_icon

DATA_PATH = Path("data.json")

# Common care tasks offered in "Schedule a Task" dropdowns, covering every
# category task_type_icon() recognizes, plus "Other (custom)" for anything else.
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
    "Brush Coat",
    "Wash / Bath",
    "Hair Cut",
    "Trim Nails",
    "Ear Cleaning",
    "Teeth Brushing",
    "Playtime",
]

# Which task_type_icon() emoji belong to each "Book a Service" category.
# Feeding (🍖) and anything task_type_icon() can't categorize (🐾) don't have
# an obvious home among the 6 categories, so they land under Special
# Services. Sitting and Training have no matching task types yet — their
# pages are placeholders until tasks like "Boarding" or "Training Session"
# get added to COMMON_TASK_TITLES and TASK_TYPE_ICONS.
SERVICE_CATEGORY_ICONS = {
    "grooming": {"👂", "🦷", "💅", "✂️", "🧼", "🪮"},
    "walking": {"🐕"},
    "veterinary": {"💊", "🏥"},
    "special_services": {"🍖", "🐾"},
}

# Title-dropdown options offered on each category's "quick add" form —
# a subset of COMMON_TASK_TITLES relevant to that specific category.
CATEGORY_TASK_TITLES = {
    "grooming": ["Brush Coat", "Wash / Bath", "Hair Cut", "Trim Nails", "Ear Cleaning", "Teeth Brushing"],
    "walking": ["Morning Walk", "Afternoon Walk", "Evening Walk", "Playtime"],
    "veterinary": ["Give Medication", "Heartworm Prevention", "Vet Appointment"],
    "special_services": ["Breakfast", "Lunch", "Dinner"],
}


def get_owner() -> Owner:
    """Return the session's owner, loading it from data.json once if needed."""
    if "owner" not in st.session_state:
        if DATA_PATH.exists():
            st.session_state.owner = Owner.load_from_json(str(DATA_PATH))
        else:
            st.session_state.owner = Owner("Jordan")
    return st.session_state.owner


def get_scheduler() -> Scheduler:
    """Return a Scheduler for the session's owner."""
    return Scheduler(get_owner())


def save_owner(owner: Owner) -> None:
    """Persist the owner to data.json — call after any mutation, on every page."""
    owner.save_to_json(str(DATA_PATH))


def task_rows(task_pairs):
    """Convert scheduler task pairs into table-friendly dictionaries."""
    return [
        {
            "Type": task_type_icon(task.title),
            "Time": format_time_12h(task.time),
            "Pet": f"{pet_species_icon(pet.species)} {pet.name}",
            "Species": pet.species,
            "Task": task.title,
            "Duration": task.duration_minutes,
            "Priority": task.priority,
            "Frequency": task.frequency,
            "Due Date": task.due_date.isoformat(),
            "Status": "✅ Done" if task.completed else "⏳ Open",
        }
        for pet, task in task_pairs
    ]


def tasks_in_category(owner: Owner, category: str):
    """Return every (pet, task) pair whose task_type_icon() belongs to a service category."""
    icons = SERVICE_CATEGORY_ICONS.get(category, set())
    return [
        (pet, task)
        for pet, task in owner.all_tasks()
        if task_type_icon(task.title) in icons
    ]


def render_category_page(category: str, display_name: str, icon: str) -> None:
    """Render a full "Book a Service" category page: quick-add form, filtered
    schedule, and a complete-task action, all scoped to this category.

    Full editing/deleting/reopening of any task still lives on the "My Pets
    & Schedule" page rather than being duplicated on every category page.
    """
    owner = get_owner()
    scheduler = get_scheduler()

    st.title(f"{icon} {display_name}")

    category_tasks = scheduler.sort_by_time(tasks_in_category(owner, category))
    title_options = CATEGORY_TASK_TITLES.get(category, [])

    if not owner.pets:
        st.warning('Add a pet from "My Pets & Schedule" before scheduling tasks here.')
    elif not title_options:
        st.info(
            f"{display_name} isn't wired up to specific task types yet — "
            'add pets and tasks from "My Pets & Schedule" instead.'
        )
    else:
        st.subheader(f"Schedule a {display_name} Task")
        with st.form(f"add_{category}_task_form", clear_on_submit=True):
            # Index-based, then re-fetch owner.pets[i] fresh — st.selectbox()
            # isn't guaranteed to hand back the same live object across
            # reruns, and add_task() mutates a list on that object, so a
            # copy would silently lose the new task.
            selected_pet_index = st.selectbox(
                "Pet",
                range(len(owner.pets)),
                format_func=lambda i: f"{pet_species_icon(owner.pets[i].species)} {owner.pets[i].name}",
            )
            title = st.selectbox("Task", title_options)

            st.write("Time")
            hour_col, minute_col, period_col = st.columns(3)
            with hour_col:
                hour_12 = st.selectbox(
                    "Hour", list(range(1, 13)), index=7, label_visibility="collapsed"
                )
            with minute_col:
                minute = st.selectbox(
                    "Minute", ["00", "15", "30", "45"], label_visibility="collapsed"
                )
            with period_col:
                period = st.selectbox("AM/PM", ["AM", "PM"], label_visibility="collapsed")

            duration = st.number_input(
                "Duration (minutes)", min_value=1, max_value=240, value=20
            )
            priority = st.selectbox("Priority", ["high", "medium", "low"])
            frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
            submitted = st.form_submit_button(f"Add {display_name} task")

        if submitted:
            hour_24 = hour_12 % 12
            if period == "PM":
                hour_24 += 12
            selected_pet = owner.pets[selected_pet_index]
            selected_pet.add_task(
                Task(
                    title=title,
                    time=f"{hour_24:02d}:{minute}",
                    duration_minutes=int(duration),
                    priority=priority,
                    frequency=frequency,
                )
            )
            st.success(f"Added {title} for {selected_pet.name}.")
            st.rerun()

    st.divider()
    st.subheader(f"{display_name} Schedule")
    if category_tasks:
        st.table(task_rows(category_tasks))
    else:
        st.info(f"No {display_name.lower()} tasks yet.")

    open_category_tasks = [pair for pair in category_tasks if not pair[1].completed]
    if open_category_tasks:
        st.subheader("Complete a Task")
        selected_pair = st.selectbox(
            "Open task",
            open_category_tasks,
            format_func=lambda pair: f"{pet_species_icon(pair[0].species)} {pair[0].name} | {pair[1].title}",
            key=f"{category}_complete_select",
        )
        if st.button("Mark complete", key=f"{category}_complete_button"):
            complete_pet, complete_task = selected_pair
            scheduler.mark_task_complete(complete_pet.name, complete_task.title)
            st.success(f"Completed {complete_task.title}.")
            st.rerun()

    save_owner(owner)
    st.caption('Full editing, deleting, and reopening tasks lives on "My Pets & Schedule".')


def render_placeholder_page(display_name: str, icon: str) -> None:
    """Render a clearly-labeled "coming soon" page for a service category that
    doesn't have matching task types in TASK_TYPE_ICONS yet."""
    st.title(f"{icon} {display_name}")
    st.info(
        f"{display_name} isn't wired up to specific task types yet — this page "
        f'is a placeholder for a future update. In the meantime, you can track '
        f'anything {display_name.lower()}-related as a custom task from '
        f'"My Pets & Schedule".'
    )
    st.page_link("pages/pets_and_schedule.py", label="Go to My Pets & Schedule", icon="🐾")
