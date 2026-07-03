from collections import Counter, defaultdict
from datetime import date

import pandas as pd
import streamlit as st

from app_common import get_clinic, get_owners, get_scheduler, task_rows

SERVICE_LINKS = [
    ("🛁", "Grooming", "pages/grooming.py"),
    ("🏠", "Sitting", "pages/sitting.py"),
    ("🎓", "Training", "pages/training.py"),
    ("🐕", "Walking", "pages/walking.py"),
    ("🍖", "Dog Cafes", "pages/special_services.py"),
    ("👥", "Staff", "pages/staff.py"),
]

SERVICE_CATEGORIES = {
    "grooming": "Grooming",
    "sitting": "Sitting",
    "training": "Training",
    "walking": "Walking",
    "special_services": "Dog Cafes",
}


def iter_service_pairs(owners):
    for owner in owners:
        for pet in owner.pets:
            for task in pet.tasks:
                if task.category in SERVICE_CATEGORIES:
                    yield pet, task


owners = get_owners()
clinic = get_clinic()
scheduler = get_scheduler()
service_pairs = list(iter_service_pairs(owners))
today = date.today()

st.title("🛎️ Book a Service Dashboard")
st.caption("A service-first overview across booking pages, task volume, and staff coverage.")

metric_cols = st.columns(4)
metric_cols[0].metric("Bookable sections", len(SERVICE_LINKS) - 1)
metric_cols[1].metric("Active staff", sum(1 for member in clinic.staff if member.active))
metric_cols[2].metric("Service bookings", len(service_pairs))
metric_cols[3].metric(
    "Today's bookings",
    sum(1 for _, task in service_pairs if task.due_date == today and not task.completed),
)

st.subheader("Quick Actions")
action_cols = st.columns(3)
for index, (icon, label, path) in enumerate(SERVICE_LINKS):
    with action_cols[index % 3]:
        with st.container(border=True):
            st.markdown(
                f"<div style='text-align:center; font-size:2rem;'>{icon}</div>",
                unsafe_allow_html=True,
            )
            st.page_link(path, label=label, use_container_width=True)

st.divider()
chart_cols = st.columns(2)

with chart_cols[0]:
    st.subheader("Bookings by Section")
    section_counts = Counter(task.category for _, task in service_pairs if task.category in SERVICE_CATEGORIES)
    if section_counts:
        section_df = pd.DataFrame(
            {"Bookings": [section_counts[key] for key in SERVICE_CATEGORIES.keys()]},
            index=list(SERVICE_CATEGORIES.values()),
        )
        st.bar_chart(section_df)
    else:
        st.info("No service bookings yet.")

with chart_cols[1]:
    st.subheader("Upcoming Bookings")
    upcoming_counts = defaultdict(int)
    for _, task in service_pairs:
        if task.completed or task.due_date < today:
            continue
        upcoming_counts[task.due_date] += 1
    if upcoming_counts:
        upcoming_days = sorted(upcoming_counts.keys())[:7]
        upcoming_df = pd.DataFrame(
            {"Bookings": [upcoming_counts[day] for day in upcoming_days]},
            index=[day.strftime("%b %d") for day in upcoming_days],
        )
        st.bar_chart(upcoming_df)
    else:
        st.info("No upcoming service bookings yet.")

st.divider()
st.subheader("Today's Service Bookings")
todays_service_pairs = [
    pair for pair in scheduler.sort_by_time(service_pairs) if pair[1].due_date == today and not pair[1].completed
]
if todays_service_pairs:
    st.table(task_rows(todays_service_pairs))
else:
    st.info("No service bookings due today.")

st.divider()
st.subheader("Next Service Bookings")
upcoming_service_pairs = [
    pair
    for pair in sorted(service_pairs, key=lambda pair: (pair[1].due_date, pair[1].time))
    if pair[1].due_date >= today and not pair[1].completed
][:8]
if upcoming_service_pairs:
    st.table(task_rows(upcoming_service_pairs))
else:
    st.caption("Nothing upcoming yet.")

st.caption("Use the service pages to add bookings, and the Staff page to manage who handles them.")
