import streamlit as st
from utils.supabase_client import supabase
from utils.supabase_admin_client import supabase_admin
from utils.class_list import CLASS_LIST
from utils.branding import show_header

st.set_page_config(page_title="Admin Dashboard", page_icon="utils/logo.jpg")

# Guard: only logged-in admins can see this page
if st.session_state.get("role") != "admin":
    st.warning("Please log in as an admin (on the main page) to view this dashboard.")
    st.stop()

show_header("🛠️ Admin Dashboard")

tab1, tab2, tab3, tab4 = st.tabs(
    ["Add Student", "All Students", "Add Teacher / Parent", "All Staff"]
)

# --- Add Student ---
with tab1:
    with st.form("add_student"):
        full_name = st.text_input("Student full name")
        student_class = st.selectbox("Class", CLASS_LIST)
        submitted = st.form_submit_button("Add Student")
        if submitted:
            supabase.table("students").insert(
                {"full_name": full_name, "class": student_class}
            ).execute()
            st.success(f"Added {full_name}")

# --- All Students ---
with tab2:
    students = supabase.table("students").select("*").execute()
    st.dataframe(students.data)

# --- Add Teacher / Parent (creates a real login, no need to touch Supabase) ---
with tab3:
    st.write("Create a login for a teacher or parent. They'll use this email/password to sign in.")
    with st.form("add_staff"):
        staff_role = st.selectbox("This person is a", ["teacher", "parent"])
        staff_name = st.text_input("Full name")
        staff_email = st.text_input("Email")
        staff_password = st.text_input("Temporary password", type="password")
        submitted = st.form_submit_button("Create Login")
        if submitted:
            try:
                result = supabase_admin.auth.admin.create_user(
                    {
                        "email": staff_email,
                        "password": staff_password,
                        "email_confirm": True,  # skip email verification step
                    }
                )
                new_user_id = result.user.id
                supabase_admin.table("profiles").insert(
                    {
                        "id": new_user_id,
                        "full_name": staff_name,
                        "role": staff_role,
                    }
                ).execute()
                st.success(f"{staff_role.title()} login created for {staff_name} ({staff_email})")
            except Exception as e:
                st.error(f"Could not create login: {e}")

# --- All Staff ---
with tab4:
    profiles = (
        supabase_admin.table("profiles")
        .select("*")
        .in_("role", ["teacher", "parent"])
        .execute()
    )
    st.dataframe(profiles.data)
