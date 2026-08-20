import streamlit as st
from utils.supabase_client import supabase
from utils.branding import show_header
from utils.fee_status import get_fee_status

st.set_page_config(page_title="Parent Dashboard", page_icon="utils/logo.jpg")

if st.session_state.get("role") != "parent":
    st.warning("Please log in as a parent (on the main page) to view this dashboard.")
    st.stop()

show_header("👪 Parent Dashboard")

st.info(
    "This is a starting template. Once students are linked to a parent_id, "
    "this will automatically show only your own children instead of everyone."
)

st.subheader("Fee Status")
status_rows = get_fee_status(supabase)
if status_rows:
    child_name = st.selectbox(
        "Select your child's name", [r["full_name"] for r in status_rows]
    )
    child_status = next(r for r in status_rows if r["full_name"] == child_name)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Fee", f"Rs. {child_status['total_fee']}")
    col2.metric("Paid", f"Rs. {child_status['paid']}")
    col3.metric("Remaining", f"Rs. {child_status['remaining']}")
else:
    st.info("No students found yet.")

st.divider()

st.subheader("Attendance")
attendance = supabase.table("attendance").select("*").execute().data
st.dataframe(attendance)
