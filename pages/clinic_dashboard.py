from collections import Counter, defaultdict

import pandas as pd
import streamlit as st

from app_common import get_clinic, get_owners, render_live_clock

owners = get_owners()
clinic = get_clinic()

st.title("🏥 Clinic Dashboard")
st.caption("A clinic-wide view across every owner's pets — not scoped to one owner.")
render_live_clock("Clinic dashboard")
st.image("assets/clinic_dashboard_homepage.png", use_container_width=True)

stat_cols = st.columns(4)
stat_cols[0].metric("Doctors", len(clinic.doctors))
stat_cols[1].metric("Patients", sum(len(owner.pets) for owner in owners))
stat_cols[2].metric("Appointments", len(clinic.appointments))
stat_cols[3].metric("Income", f"${clinic.income():.2f}")

st.divider()
chart_cols = st.columns(2)

with chart_cols[0]:
    st.subheader("Hospital Traffic (Monthly)")
    monthly_counts = defaultdict(int)
    for appointment in clinic.appointments:
        monthly_counts[appointment.date.replace(day=1)] += 1
    if monthly_counts:
        sorted_months = sorted(monthly_counts.keys())
        traffic_df = pd.DataFrame(
            {"Appointments": [monthly_counts[month] for month in sorted_months]},
            index=[month.strftime("%b %Y") for month in sorted_months],
        )
        st.bar_chart(traffic_df)
    else:
        st.info("No appointments yet.")

with chart_cols[1]:
    st.subheader("Patient Demographics")
    species_counts = Counter(pet.species for owner in owners for pet in owner.pets)
    if species_counts:
        demographics_df = pd.DataFrame(
            {"Pets": list(species_counts.values())}, index=list(species_counts.keys())
        )
        st.bar_chart(demographics_df)
    else:
        st.info("No patients yet.")
