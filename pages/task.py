from datetime import date

import streamlit as st

from app_common import get_combined_owner, get_scheduler, render_live_clock, task_rows

TASK_LINKS = [
    ("📊", "Pet Profile", "pages/dashboard.py"),
    ("🗓️", "Calendar", "pages/calendar.py"),
    ("🧾", "Patients", "pages/patients.py"),
    ("🛁", "Grooming", "pages/grooming.py"),
    ("🏠", "Sitting", "pages/sitting.py"),
    ("🎓", "Training", "pages/training.py"),
    ("🐕", "Walking", "pages/walking.py"),
    ("🍖", "Dog Cafes", "pages/special_services.py"),
    ("🩺", "Veterinary", "pages/appointments.py"),
]


owner = get_combined_owner()
scheduler = get_scheduler()
today = date.today()

st.title("📝 Task Hub")
st.caption("A single place to review today's work, jump into task setup, and see what is coming next.")
render_live_clock("Task Hub")

metric_cols = st.columns(4)
metric_cols[0].metric("Pets", len(owner.pets))
metric_cols[1].metric("Open today", len(scheduler.todays_schedule()))
metric_cols[2].metric("Next urgent", 1 if scheduler.next_urgent_task() else 0)
metric_cols[3].metric("Top priorities", len(scheduler.top_priorities()))

st.subheader("Task Setup")
link_cols = st.columns(3)
for index, (icon, label, path) in enumerate(TASK_LINKS):
    with link_cols[index % 3]:
        with st.container(border=True):
            st.markdown(f"<div style='text-align:center; font-size:2rem;'>{icon}</div>", unsafe_allow_html=True)
            st.page_link(path, label=label, use_container_width=True)

st.divider()
st.subheader("Today's Highlights")
today_tasks = scheduler.todays_schedule()
if today_tasks:
    st.table(task_rows(today_tasks))
else:
    st.info("No tasks are due today.")

st.divider()
left, right = st.columns(2)

with left:
    st.subheader("Next Urgent Task")
    urgent = scheduler.next_urgent_task()
    if urgent:
        pet, task = urgent
        st.table(task_rows([(pet, task)]))
    else:
        st.caption("Nothing urgent yet.")

with right:
    st.subheader("Top 3 Priorities")
    top_tasks = scheduler.top_priorities()
    if top_tasks:
        st.table(task_rows(top_tasks))
    else:
        st.caption("No tasks to rank yet.")

st.divider()
st.subheader("Upcoming Tasks")
upcoming = scheduler.upcoming_tasks(8)
if upcoming:
    st.table(task_rows(upcoming))
else:
    st.info("No upcoming tasks yet.")

st.caption("Use the service pages to add tasks, the calendar to browse the month, and Patients to restore or manage the roster.")
