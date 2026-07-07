"""Booking-form rendering and task creation for a category page."""

from datetime import date

import streamlit as st

from ai_system import advise_service
from constants import CATEGORY_TASK_TITLES
from pawpal_system import Task
from pickers import render_dog_cafe_menu_picker, render_veterinary_reason_picker
from state import get_combined_owner, save_owner


def _default_task_selection(category: str, title_options: list[str]) -> list[str]:
    """Pick the most helpful default tasks for a category."""
    if category == "grooming":
        preferred = ["Brush Coat", "Wash / Bath", "Trim Nails"]
        return [title for title in preferred if title in title_options] or title_options[:1]
    return title_options[:1]


def render_category_booking_form(category: str, display_name: str, active_staff, selected_owner, selected_pet_index):
    """Render the task booking form and handle task creation."""
    title_options = CATEGORY_TASK_TITLES.get(category, [])
    if not title_options:
        return

    selected_pet = selected_owner.pets[selected_pet_index]
    advice = advise_service(category, selected_pet.species, title_options)
    if advice is not None:
        st.info(f"AI suggestion: {advice.explanation}")
        default_titles = advice.guide.recommended_titles
    else:
        default_titles = _default_task_selection(category, title_options)

    if category == "veterinary":
        selected_titles = [st.selectbox("Task", title_options, key=f"{category}_title_select")]
        selected_species = selected_pet.species
        reason = render_veterinary_reason_picker(selected_titles[0], selected_species, key_prefix=category)
    elif category == "special_services":
        selected_titles = [st.selectbox("Task", title_options, key=f"{category}_title_select")]
        reason = render_dog_cafe_menu_picker()
    else:
        selected_titles = st.multiselect(
            "Task(s)",
            title_options,
            default=[title for title in default_titles if title in title_options] or title_options[:1],
            key=f"{category}_title_select",
        )
        st.text_input("Reason", value="—", disabled=True, key=f"{category}_disabled_reason")
        reason = None

    if not selected_titles:
        st.info("Pick at least one task to continue.")
        return

    with st.form(f"add_{category}_task_form", clear_on_submit=True):
        date_col, staff_col = st.columns(2)
        with date_col:
            appt_date = st.date_input("Date", value=date.today(), key=f"{category}_date")
        with staff_col:
            if active_staff:
                staff_labels = [
                    f"{member.full_name} ({member.role})" if member.role else member.full_name
                    for member in active_staff
                ]
                staff_index = st.selectbox("Assigned staff", range(len(active_staff)), format_func=lambda i: staff_labels[i], key=f"{category}_staff_select")
            else:
                staff_index = None
                st.caption("No active staff in this section — add some on the Staff page.")

        st.write("Time")
        hour_col, minute_col, period_col = st.columns(3)
        with hour_col:
            hour_12 = st.selectbox("Hour", list(range(1, 13)), index=7, label_visibility="collapsed")
        with minute_col:
            minute = st.selectbox("Minute", ["00", "15", "30", "45"], label_visibility="collapsed")
        with period_col:
            period = st.selectbox("AM/PM", ["AM", "PM"], label_visibility="collapsed")

        if category == "special_services":
            duration, priority = 60, "medium"
            submitted = st.form_submit_button("Dog Cafe RSVP")
        else:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
            priority = st.selectbox("Priority", ["high", "medium", "low"])
            submitted = st.form_submit_button(f"Add {display_name} task(s)")

    if submitted:
        hour_24 = hour_12 % 12
        if period == "PM":
            hour_24 += 12
        time_str = f"{hour_24:02d}:{minute}"
        assignee = active_staff[staff_index].full_name if staff_index is not None else None
        conflict = any(t.time == time_str and t.due_date == appt_date and not t.completed for t in selected_pet.tasks)
        if conflict:
            st.session_state["ui_alert_warning"] = f"⚠️ Schedule Conflict: {selected_pet.name} already has a task scheduled at {time_str} on {appt_date.isoformat()}. Double-booking detected!"

        for title in selected_titles:
            selected_pet.add_task(
                Task(
                    title=title,
                    time=time_str,
                    duration_minutes=int(duration),
                    priority=priority,
                    notes=reason,
                    due_date=appt_date,
                    category=category,
                    assignee=assignee,
                )
            )
        save_owner(get_combined_owner())
        if len(selected_titles) == 1:
            success_message = f"Added {selected_titles[0]} for {selected_pet.name}."
        else:
            success_message = f"Added {len(selected_titles)} tasks for {selected_pet.name}."
        if reason:
            success_message = f"Added {', '.join(selected_titles)} ({reason}) for {selected_pet.name}."
        st.session_state["ui_alert_success"] = success_message
        st.rerun()
