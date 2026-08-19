from datetime import date
import streamlit as st
from utils.supabase_client import supabase
from utils.class_list import CLASS_LIST
from utils.branding import show_header

st.set_page_config(page_title="Teacher Dashboard", page_icon="utils/logo.jpg")

if st.session_state.get("role") != "teacher":
    st.warning("Please log in as a teacher (on the main page) to view this dashboard.")
    st.stop()

show_header("🧑‍🏫 Teacher Dashboard")

selected_class = st.selectbox("Select class", CLASS_LIST)

# --- Attendance ---
st.subheader(f"Mark Attendance — {selected_class}")
students = (
    supabase.table("students")
    .select("*")
    .eq("class", selected_class)
    .execute()
    .data
)
attendance_date = st.date_input("Date", value=date.today())

if students:
    with st.form("attendance_form"):
        statuses = {}
        for s in students:
            statuses[s["id"]] = st.selectbox(
                s["full_name"], ["Present", "Absent"], key=f"att_{s['id']}"
            )
        submitted = st.form_submit_button("Save Attendance")
        if submitted:
            for student_id, status in statuses.items():
                supabase.table("attendance").insert(
                    {
                        "student_id": student_id,
                        "class": selected_class,
                        "date": str(attendance_date),
                        "status": status,
                    }
                ).execute()
            st.success("Attendance saved!")
else:
    st.info(f"No students found in {selected_class} yet. Ask the admin to add them first.")

st.divider()

# --- Homework upload ---
st.subheader(f"Upload Homework — {selected_class}")
with st.form("homework_form"):
    title = st.text_input("Homework title")
    file = st.file_uploader("Choose a file")
    submitted = st.form_submit_button("Upload")
    if submitted and file:
        file_bytes = file.read()
        path = f"{selected_class}/{file.name}"
        supabase.storage.from_("homework").upload(path, file_bytes)
        file_url = supabase.storage.from_("homework").get_public_url(path)
        supabase.table("homework").insert(
            {"title": title, "class": selected_class, "file_url": file_url}
        ).execute()
        st.success("Homework uploaded!")
