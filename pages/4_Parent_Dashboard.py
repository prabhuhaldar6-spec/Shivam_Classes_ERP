import streamlit as st
from utils.supabase_client import supabase
from utils.branding import show_header

st.set_page_config(page_title="Parent Dashboard", page_icon="utils/logo.jpg")

if st.session_state.get("role") != "parent":
    st.warning("Please log in as a parent (on the main page) to view this dashboard.")
    st.stop()

show_header("👪 Parent Dashboard")

st.info(
    "This is a starting template. Once students are linked to a parent_id, "
    "filter the queries below to that parent's own children only."
)

st.subheader("Fees")
fees = supabase.table("fees").select("*").execute().data
st.dataframe(fees)

st.subheader("Attendance")
attendance = supabase.table("attendance").select("*").execute().data
st.dataframe(attendance)
