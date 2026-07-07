"""Shared 'today's schedule' and 'monthly calendar' page bodies.

Book a Service and Veterinarian each get their own today/monthly schedule
page, scoped to their own task categories, without duplicating the same
filter/complete/delete/calendar-grid UI twice.
"""

import calendar as calendar_module
import html as html_escaping
from collections import defaultdict
from datetime import date

import streamlit as st

from availability import freed_slot_label
from pawpal_system import format_time_12h, task_type_icon
from app_common import (
    PET_TIMELINE_COLORS,
    get_combined_owner,
    get_owners,
    get_scheduler,
    render_live_clock,
    save_owner,
    task_pair_label,
    task_rows,
    tasks_in_category,
)

MAX_BADGES_PER_DAY = 3


def _scoped_pairs(owner, categories):
    """All (pet, task) pairs whose category is in `categories` (or every task
    if `categories` is None), reusing tasks_in_category's legacy-icon
    fallback for tasks saved before the category field existed."""
    if categories is None:
        return owner.all_tasks()
    seen = set()
    pairs = []
    for category in categories:
        for pet, task in tasks_in_category(owner, category):
            if id(task) not in seen:
                seen.add(id(task))
                pairs.append((pet, task))
    return pairs


def _add_hours(time_str: str, hours: int) -> str:
    hour, minute = (int(part) for part in time_str.split(":"))
    hour = min(hour + hours, 23)
    return f"{hour:02d}:{minute:02d}"


def render_todays_schedule_page(
    *,
    page_icon: str,
    page_title: str,
    caption: str,
    categories: set[str] | None,
    include_reason: bool,
    windowed: bool = False,
    window_hours: int = 2,
) -> None:
    """Render a full today's-schedule page scoped to the given task categories."""
    owner = get_combined_owner()
    scheduler = get_scheduler()
    real_owners = get_owners()
    scoped_pairs = _scoped_pairs(owner, categories)

    st.title(f"{page_icon} {page_title}")
    st.caption(caption)
    render_live_clock(page_title)

    pet_filter = st.sidebar.selectbox(
        "Filter by pet", ["All pets"] + sorted({pet.name for pet in owner.pets})
    )
    status_filter = st.sidebar.selectbox("Filter by status", ["Open", "Done", "All"])

    completed_filter = None
    if status_filter == "Open":
        completed_filter = False
    elif status_filter == "Done":
        completed_filter = True

    pet_name = None if pet_filter == "All pets" else pet_filter
    today = date.today()

    def _matches(pet, task) -> bool:
        if pet_name and pet.name.lower() != pet_name.lower():
            return False
        if completed_filter is not None and task.completed is not completed_filter:
            return False
        return True

    todays_tasks = scheduler.sort_by_time(
        [pair for pair in scoped_pairs if pair[1].due_date == today and _matches(*pair)]
    )

    st.subheader(f"{page_icon} {page_title}")
    if todays_tasks:
        if windowed:
            expanded_key = f"{page_title}_schedule_expanded"
            if expanded_key not in st.session_state:
                st.session_state[expanded_key] = False

            if st.session_state[expanded_key]:
                visible_tasks = todays_tasks
            else:
                window_end = _add_hours(todays_tasks[0][1].time, window_hours)
                visible_tasks = [pair for pair in todays_tasks if pair[1].time <= window_end]

            st.table(task_rows(visible_tasks, include_reason=include_reason))
            hidden_count = len(todays_tasks) - len(visible_tasks)

            if st.session_state[expanded_key]:
                if st.button("Show less", key=f"{page_title}_show_less"):
                    st.session_state[expanded_key] = False
                    st.rerun()
            elif hidden_count > 0:
                if st.button(f"Show more ({hidden_count} more today)", key=f"{page_title}_show_more"):
                    st.session_state[expanded_key] = True
                    st.rerun()
        else:
            st.table(task_rows(todays_tasks, include_reason=include_reason))
    else:
        st.info("No tasks due today match the current filters.")

    st.markdown("**❗ High Priority First**")
    high_priority_today = scheduler.sort_by_priority_then_time(todays_tasks)
    if high_priority_today:
        st.table(task_rows(high_priority_today, include_reason=include_reason))
    else:
        st.info("No tasks due today match the current filters.")

    st.markdown("**🚨 Next Urgent Task**")
    urgent = scheduler.next_urgent_task(todays_tasks)
    if urgent:
        st.table(task_rows([urgent], include_reason=include_reason))
    else:
        st.info("No tasks due today match the current filters.")

    st.markdown("**⭐ Today's Top 3 Priorities**")
    top_priorities = scheduler.top_priorities(3, todays_tasks)
    if top_priorities:
        st.table(task_rows(top_priorities, include_reason=include_reason))
    else:
        st.info("No tasks due today match the current filters.")

    st.markdown("**⚠️ Conflict Warnings**")
    scoped_open_tasks = [pair for pair in scoped_pairs if not pair[1].completed]
    conflicts = scheduler.detect_conflicts(scoped_open_tasks)
    if conflicts:
        for warning in conflicts:
            st.warning(warning)
    else:
        st.success("No open task conflicts.")

    if owner.pets:
        st.subheader("Complete a Task")
        open_tasks = scheduler.sort_by_time(scoped_open_tasks)
        if open_tasks:
            open_labels = [
                task_pair_label(i, pet, task, real_owners)
                for i, (pet, task) in enumerate(open_tasks)
            ]
            complete_index = st.selectbox(
                "Open task",
                range(len(open_tasks)),
                format_func=lambda i: open_labels[i],
                key=f"{page_title}_complete_select",
            )
            if st.button("Mark complete", key=f"{page_title}_complete_button"):
                open_pet, open_task = open_tasks[complete_index]
                open_task.mark_complete()
                next_task = open_task.next_occurrence(completed_on=date.today())
                if next_task is not None:
                    open_pet.add_task(next_task)
                save_owner(owner)
                st.success(f"Completed {open_task.title}.")
                st.rerun()
        else:
            st.info("All tasks are complete.")

        st.subheader("Delete or Reopen a Task")
        all_tasks = scheduler.sort_by_time(scoped_pairs)
        if all_tasks:
            all_task_labels = [
                f"{task_pair_label(i, pet, task, real_owners)} ({'Done' if task.completed else 'Open'})"
                for i, (pet, task) in enumerate(all_tasks)
            ]
            selected_task_index = st.selectbox(
                "Task",
                range(len(all_tasks)),
                format_func=lambda i: all_task_labels[i],
                key=f"{page_title}_task_select",
            )
            preview_pet, preview_task = all_tasks[selected_task_index]

            col1, col2 = st.columns(2)
            with col1:
                if preview_task.completed and st.button("Reopen task", key=f"{page_title}_reopen"):
                    _, task_to_reopen = all_tasks[selected_task_index]
                    task_to_reopen.mark_incomplete()
                    save_owner(owner)
                    st.success(f"Reopened {task_to_reopen.title}.")
                    st.rerun()
            with col2:
                if st.button("Delete task", key=f"{page_title}_delete"):
                    pet_to_edit_tasks, task_to_delete = all_tasks[selected_task_index]
                    pet_to_edit_tasks.remove_task(task_to_delete)
                    save_owner(owner)
                    message = f"Deleted {task_to_delete.title}."
                    if task_to_delete.assignee:
                        freed = freed_slot_label(
                            task_to_delete.time,
                            task_to_delete.duration_minutes,
                            task_to_delete.assignee,
                            format_time_12h,
                        )
                        message += f" This frees up {freed}."
                    st.success(message)
                    st.rerun()
        else:
            st.info("No tasks yet.")

    st.caption("Data is auto-saved to `data.json` after every change, so it persists between app runs.")


def _render_month_grid(owner, scoped_pairs, target_year: int, target_month: int) -> None:
    """Render a Mon-Sun month grid with a colored badge per task, as custom
    HTML/CSS — Streamlit has no built-in calendar widget."""
    weeks = calendar_module.Calendar(firstweekday=0).monthdatescalendar(target_year, target_month)
    today = date.today()

    tasks_by_date = defaultdict(list)
    for pet, task in scoped_pairs:
        tasks_by_date[task.due_date].append((pet, task))

    pet_color = {
        pet.name: PET_TIMELINE_COLORS[index % len(PET_TIMELINE_COLORS)]
        for index, pet in enumerate(owner.pets)
    }

    header_html = "".join(
        f'<div class="pp-cal-header">{abbr}</div>'
        for abbr in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    )

    weeks_html = ""
    for week in weeks:
        week_html = ""
        for day in week:
            day_tasks = tasks_by_date.get(day, [])
            badges_html = ""
            for pet, task in day_tasks[:MAX_BADGES_PER_DAY]:
                tooltip = html_escaping.escape(
                    f"{pet.name}: {task.title} at {format_time_12h(task.time)}"
                )
                badge_label = html_escaping.escape(pet.name)
                badges_html += (
                    f'<div class="pp-cal-badge" style="background:{pet_color[pet.name]};" '
                    f'title="{tooltip}">{task_type_icon(task.title)} {badge_label}</div>'
                )
            overflow = len(day_tasks) - MAX_BADGES_PER_DAY
            if overflow > 0:
                badges_html += f'<div class="pp-cal-more">+{overflow} more</div>'

            cell_classes = "pp-cal-cell"
            if day.month != target_month:
                cell_classes += " pp-cal-outside"
            if day == today:
                cell_classes += " pp-cal-today"

            week_html += (
                f'<div class="{cell_classes}"><div class="pp-cal-daynum">{day.day}</div>'
                f"{badges_html}</div>"
            )
        weeks_html += f'<div class="pp-cal-week">{week_html}</div>'

    calendar_html = f"""
    <style>
    .pp-cal-header {{ flex:1; text-align:center; font-size:0.75rem; color:#888; padding:4px 0; }}
    .pp-cal-week {{ display:flex; gap:4px; margin-bottom:4px; }}
    .pp-cal-cell {{ flex:1; min-height:80px; background:rgba(255,255,255,0.05); border-radius:8px;
                    padding:6px; display:flex; flex-direction:column; gap:2px; box-sizing:border-box; }}
    .pp-cal-outside {{ opacity:0.35; }}
    .pp-cal-today {{ border:2px solid #3B5BDB; }}
    .pp-cal-daynum {{ font-size:0.8rem; color:#ccc; font-weight:600; margin-bottom:2px; }}
    .pp-cal-badge {{ border-radius:6px; color:white; font-size:0.65rem; padding:1px 4px;
                      overflow:hidden; white-space:nowrap; text-overflow:ellipsis; }}
    .pp-cal-more {{ font-size:0.65rem; color:#888; }}
    </style>
    <div style="display:flex; gap:4px; margin-bottom:4px;">{header_html}</div>
    {weeks_html}
    """
    st.markdown(calendar_html, unsafe_allow_html=True)


def render_monthly_schedule_page(
    *,
    page_icon: str,
    page_title: str,
    caption: str,
    categories: set[str] | None,
    session_key_prefix: str,
    include_reason: bool,
) -> None:
    """Render a full month-calendar page scoped to the given task categories."""
    owner = get_combined_owner()
    scheduler = get_scheduler()

    st.title(f"{page_icon} {page_title}")
    st.caption(caption)
    render_live_clock(page_title)

    if not owner.pets:
        st.info("Add a pet to see their calendar here.")
        st.page_link("pages/patients.py", label="Go to Patients", icon="🧾")
        return

    offset_key = f"{session_key_prefix}_calendar_month_offset"
    if offset_key not in st.session_state:
        st.session_state[offset_key] = 0

    today = date.today()
    month_index = today.month - 1 + st.session_state[offset_key]
    target_year = today.year + month_index // 12
    target_month = month_index % 12 + 1

    nav_prev, nav_label, nav_today, nav_next = st.columns([1, 3, 1, 1])
    with nav_prev:
        if st.button("◀ Previous", key=f"{session_key_prefix}_calendar_prev"):
            st.session_state[offset_key] -= 1
            st.rerun()
    with nav_label:
        st.markdown(f"### {calendar_module.month_name[target_month]} {target_year}")
    with nav_today:
        if st.button("Today", key=f"{session_key_prefix}_calendar_today"):
            st.session_state[offset_key] = 0
            st.rerun()
    with nav_next:
        if st.button("Next ▶", key=f"{session_key_prefix}_calendar_next"):
            st.session_state[offset_key] += 1
            st.rerun()

    scoped_pairs = _scoped_pairs(owner, categories)
    _render_month_grid(owner, scoped_pairs, target_year, target_month)

    st.divider()
    st.subheader("Day Details")

    month_dates = [
        day
        for week in calendar_module.Calendar(firstweekday=0).monthdatescalendar(target_year, target_month)
        for day in week
        if day.month == target_month
    ]
    default_date = today if today in month_dates else month_dates[0]
    selected_date_index = st.selectbox(
        "View a day's tasks",
        range(len(month_dates)),
        index=month_dates.index(default_date),
        format_func=lambda i: month_dates[i].strftime("%A, %B %d"),
        key=f"{session_key_prefix}_calendar_day_select",
    )
    selected_date = month_dates[selected_date_index]

    day_tasks = scheduler.sort_by_time(
        [pair for pair in scoped_pairs if pair[1].due_date == selected_date]
    )
    if day_tasks:
        st.table(task_rows(day_tasks, include_reason=include_reason))
    else:
        st.info("No tasks scheduled for this day.")

    day_conflicts = scheduler.detect_conflicts(day_tasks)
    for warning in day_conflicts:
        st.warning(warning)

    st.caption("Data is auto-saved to `data.json` after every change, so it persists between app runs.")
