import streamlit as st

from pawpal_system import Department, Service
from app_common import get_clinic, save_clinic

clinic = get_clinic()

st.title("🏬 Departments & Services")
st.caption("Maintain the clinic's departments and the services billed under each.")

st.subheader("Departments")
with st.form("add_department_form", clear_on_submit=True):
    department_name = st.text_input("Department Name")
    department_description = st.text_input("Description")
    submitted_department = st.form_submit_button("Add Department")

if submitted_department and department_name.strip():
    if clinic.find_department(department_name.strip()):
        st.error(f"A department named '{department_name.strip()}' already exists.")
    else:
        clinic.departments.append(
            Department(department_name.strip(), department_description.strip())
        )
        save_clinic(clinic)
        st.success(f"Added {department_name.strip()}.")
        st.rerun()

if clinic.departments:
    st.table(
        [
            {"Department Name": department.name, "Description": department.description}
            for department in clinic.departments
        ]
    )

    delete_department_index = st.selectbox(
        "Delete a department",
        range(len(clinic.departments)),
        format_func=lambda i: clinic.departments[i].name,
        key="delete_department_select",
    )
    if st.button("Delete department", key="delete_department_button"):
        removed = clinic.departments.pop(delete_department_index)
        save_clinic(clinic)
        st.success(f"Deleted {removed.name}.")
        st.rerun()
else:
    st.info("No departments yet.")

st.divider()
st.subheader("Medical Services")
if not clinic.departments:
    st.warning("Add a department before adding services.")
else:
    with st.form("add_service_form", clear_on_submit=True):
        service_name = st.text_input("Service Name")
        service_department_index = st.selectbox(
            "Department",
            range(len(clinic.departments)),
            format_func=lambda i: clinic.departments[i].name,
            key="service_department_select",
        )
        service_cost = st.number_input("Cost ($)", min_value=0.0, step=1.0, value=0.0)
        submitted_service = st.form_submit_button("Add Service")

    if submitted_service and service_name.strip():
        service_department = clinic.departments[service_department_index]
        clinic.services.append(
            Service(service_name.strip(), service_department.name, float(service_cost))
        )
        save_clinic(clinic)
        st.success(f"Added {service_name.strip()}.")
        st.rerun()

if clinic.services:
    st.table(
        [
            {
                "Service Name": service.name,
                "Department": service.department_name,
                "Cost ($)": f"${service.cost:.2f}",
            }
            for service in clinic.services
        ]
    )

    delete_service_index = st.selectbox(
        "Delete a service",
        range(len(clinic.services)),
        format_func=lambda i: clinic.services[i].name,
        key="delete_service_select",
    )
    if st.button("Delete service", key="delete_service_button"):
        removed = clinic.services.pop(delete_service_index)
        save_clinic(clinic)
        st.success(f"Deleted {removed.name}.")
        st.rerun()
else:
    st.info("No services yet.")

save_clinic(clinic)
st.caption("Data is auto-saved to `clinic.json` after every change, so it persists between app runs.")
