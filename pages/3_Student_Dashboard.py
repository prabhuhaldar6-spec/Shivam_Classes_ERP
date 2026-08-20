import streamlit as st
from utils.supabase_client import supabase
from utils.class_list import CLASS_LIST
from utils.branding import show_header
from utils.fee_status import get_fee_status

st.set_page_config(page_title="Student Dashboard", page_icon="utils/logo.jpg")

if st.session_state.get("role") != "student":
    st.warning("Please log in as a student (on the main page) to view this dashboard.")
    st.stop()

show_header("🎓 Student Dashboard")

selected_class = st.selectbox("Your class", CLASS_LIST)
# NOTE: once each student login is linked to their own student_id, replace this
# manual class picker with an automatic lookup based on st.session_state.user.

st.subheader(f"Homework — {selected_class}")
homework = (
    supabase.table("homework")
    .select("*")
    .eq("class", selected_class)
    .execute()
    .data
)
if homework:
    for h in homework:
        st.write(f"**{h['title']}**")
        st.markdown(f"[Download / View file]({h['file_url']})")
else:
    st.info("No homework posted yet for this class.")

st.divider()

st.subheader(f"Attendance — {selected_class}")
students_in_class = (
    supabase.table("students")
    .select("id")
    .eq("class", selected_class)
    .execute()
    .data
)
student_ids = [s["id"] for s in students_in_class]

if student_ids:
    attendance = (
        supabase.table("attendance")
        .select("*")
        .in_("student_id", student_ids)
        .execute()
        .data
    )
    st.dataframe(attendance)
else:
    st.info("No students found in this class yet.")

st.divider()

st.subheader("My Fees")
status_rows = get_fee_status(supabase, class_filter=selected_class)
if status_rows:
    my_name = st.selectbox(
        "Select your name to see your fee status",
        [r["full_name"] for r in status_rows],
        key="fee_name_pick",
    )
    my_status = next(r for r in status_rows if r["full_name"] == my_name)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Fee", f"Rs. {my_status['total_fee']}")
    col2.metric("Paid", f"Rs. {my_status['paid']}")
    col3.metric("Remaining", f"Rs. {my_status['remaining']}")
else:
    st.info("No fee records yet for this class.")
