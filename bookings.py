"""Booking-form rendering and task creation for a category page."""

from datetime import date

import streamlit as st

from ai_applied_agentic_loop import plan_booking
from ai_system import advise_service
from availability import find_available_slots
from constants import CATEGORY_TASK_TITLES
from pawpal_system import Task, format_time_12h
from pickers import render_dog_cafe_menu_picker, render_veterinary_reason_picker
from state import get_combined_owner, save_owner


def _default_task_selection(category: str, title_options: list[str]) -> list[str]:
    """Pick the most helpful default tasks for a category."""
    if category == "grooming":
        preferred = ["Brush Coat", "Wash / Bath", "Trim Nails"]
        return [title for title in preferred if title in title_options] or title_options[:1]
    return title_options[:1]


def _render_agent_planner(category: str, selected_pet, active_staff, title_options):
    """Run the agentic booking planner on demand and show its reasoning
    trace. Returns (planned_staff_name, planned_slot_start) when the most
    recent plan succeeded and still applies to the currently selected pet,
    else (None, None)."""
    plan_key = f"{category}_agent_plan"
    plan_pet_key = f"{category}_agent_plan_pet"

    if st.button("🤖 Run Auto-Planner", key=f"{category}_run_agent"):
        plan = plan_booking(
            category=category,
            pet=selected_pet,
            title_options=title_options,
            active_staff=active_staff,
            combined_owner=get_combined_owner(),
        )
        st.session_state[plan_key] = plan
        st.session_state[plan_pet_key] = selected_pet.name

    plan = st.session_state.get(plan_key)
    if plan is None or st.session_state.get(plan_pet_key) != selected_pet.name:
        return None, None

    if plan.success:
        st.success(
            f"🤖 Agent plan: book **{plan.task_title}** with **{plan.staff_name}** "
            f"at **{format_time_12h(plan.slot_start)}**."
        )
    else:
        st.warning(f"🤖 Agent could not find a conflict-free slot for {selected_pet.name} today.")

    with st.expander("Show agent reasoning trace"):
        for step in plan.trace:
            st.markdown(f"- **{step.action}**: {step.detail}")

    if plan.success:
        return plan.staff_name, plan.slot_start
    return None, None


def _render_staff_availability(active_staff, category: str) -> None:
    """Show each active staff member's open slots today, so a cancellation
    elsewhere becomes visibly bookable before the form is even filled out."""
    if not active_staff:
        return
    today = date.today()
    combined_owner = get_combined_owner()
    with st.expander("📅 Staff availability today", expanded=False):
        for member in active_staff:
            busy = [
                (task.time, task.duration_minutes)
                for pet, task in combined_owner.all_tasks()
                if task.assignee == member.full_name
                and task.due_date == today
                and task.category == category
            ]
            slots = find_available_slots(busy)
            if not slots:
                st.caption(f"**{member.full_name}**: fully booked today")
                continue
            shown = ", ".join(f"{format_time_12h(s)}–{format_time_12h(e)}" for s, e in slots[:6])
            more = f" (+{len(slots) - 6} more)" if len(slots) > 6 else ""
            st.caption(f"**{member.full_name}**: {shown}{more}")


def render_category_booking_form(category: str, display_name: str, active_staff, selected_owner, selected_pet_index):
    """Render the task booking form and handle task creation."""
    title_options = CATEGORY_TASK_TITLES.get(category, [])
    if not title_options:
        return

    _render_staff_availability(active_staff, category)

    selected_pet = selected_owner.pets[selected_pet_index]
    planned_staff_name, planned_slot_start = _render_agent_planner(category, selected_pet, active_staff, title_options)

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
        reason = None

    if not selected_titles:
        st.info("Pick at least one task to continue.")
        return

    # Default the staff/time widgets to the agent's plan, if it found one for
    # this pet — otherwise fall back to the previous fixed defaults (first
    # staff, 8:00 AM).
    default_staff_index = 0
    if planned_staff_name:
        for i, member in enumerate(active_staff):
            if member.full_name == planned_staff_name:
                default_staff_index = i
                break

    default_hour_index, default_minute_index, default_period_index = 7, 0, 0
    if planned_slot_start:
        plan_hour_24, plan_minute = (int(part) for part in planned_slot_start.split(":"))
        default_period_index = 1 if plan_hour_24 >= 12 else 0
        plan_hour_12 = plan_hour_24 % 12 or 12
        default_hour_index = plan_hour_12 - 1
        minute_options = ["00", "15", "30", "45"]
        if f"{plan_minute:02d}" in minute_options:
            default_minute_index = minute_options.index(f"{plan_minute:02d}")

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
                staff_index = st.selectbox("Assigned staff", range(len(active_staff)), format_func=lambda i: staff_labels[i], index=default_staff_index, key=f"{category}_staff_select")
            else:
                staff_index = None
                st.caption("No active staff in this section — add some on the Staff page.")

        st.write("Time")
        hour_col, minute_col, period_col = st.columns(3)
        with hour_col:
            hour_12 = st.selectbox("Hour", list(range(1, 13)), index=default_hour_index, label_visibility="collapsed")
        with minute_col:
            minute = st.selectbox("Minute", ["00", "15", "30", "45"], index=default_minute_index, label_visibility="collapsed")
        with period_col:
            period = st.selectbox("AM/PM", ["AM", "PM"], index=default_period_index, label_visibility="collapsed")

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
