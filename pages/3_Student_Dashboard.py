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

# Try to find this exact student's own record via their login
my_user_id = st.session_state.user.id
my_student_record = (
    supabase.table("students")
    .select("*")
    .eq("profile_id", my_user_id)
    .execute()
    .data
)

if my_student_record:
    # Real per-student login — everything below is automatically scoped to them
    me = my_student_record[0]
    selected_class = me["class"]
    st.caption(f"Showing your own data — {me['full_name']}, {selected_class}")
else:
    # Fallback for students without a linked login yet — ask the teacher/admin
    # to create one for a fully personal view. Meanwhile, let them pick their class.
    st.info(
        "Your login isn't linked to a specific student record yet — ask your "
        "coaching center to link it for a fully personal view. Showing by class for now."
    )
    selected_class = st.selectbox("Your class", CLASS_LIST)
    me = None

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
if me:
    attendance = (
        supabase.table("attendance")
        .select("*")
        .eq("student_id", me["id"])
        .execute()
        .data
    )
else:
    students_in_class = (
        supabase.table("students")
        .select("id")
        .eq("class", selected_class)
        .execute()
        .data
    )
    student_ids = [s["id"] for s in students_in_class]
    attendance = (
        supabase.table("attendance")
        .select("*")
        .in_("student_id", student_ids)
        .execute()
        .data
        if student_ids
        else []
    )

if attendance:
    st.dataframe(attendance)
else:
    st.info("No attendance records yet.")

st.divider()

st.subheader("My Fees")
if me:
    status_rows = get_fee_status(supabase, class_filter=selected_class)
    my_status = next((r for r in status_rows if r["id"] == me["id"]), None)
    if my_status:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Fee", f"Rs. {my_status['total_fee']}")
        col2.metric("Paid", f"Rs. {my_status['paid']}")
        col3.metric("Remaining", f"Rs. {my_status['remaining']}")
    else:
        st.info("No fee record found.")
else:
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
