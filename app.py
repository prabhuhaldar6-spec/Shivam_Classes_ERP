import streamlit as st
from utils.supabase_client import supabase
from utils.branding import show_header

st.set_page_config(page_title="Shivam Classes ERP", page_icon="utils/logo.jpg")

# Keep track of who is logged in across page switches
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.role = None
    st.session_state.full_name = None


def login_with_email(email: str, password: str):
    try:
        result = supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
        _finish_login(result.user)
    except Exception as e:
        st.error(f"Login failed: {e}")


def login_with_phone(phone: str, password: str):
    try:
        result = supabase.auth.sign_in_with_password(
            {"phone": phone, "password": password}
        )
        _finish_login(result.user)
    except Exception as e:
        st.error(f"Login failed: {e}")


def _finish_login(user):
    # Look up this user's role (admin/teacher/student/parent) from the profiles table
    profile = (
        supabase.table("profiles")
        .select("*")
        .eq("id", user.id)
        .single()
        .execute()
    )
    st.session_state.user = user
    st.session_state.role = profile.data["role"]
    st.session_state.full_name = profile.data["full_name"]
    st.rerun()


def logout():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.session_state.role = None
    st.session_state.full_name = None
    st.rerun()


show_header()

if st.session_state.user is None:
    st.subheader("Login")

    login_method = st.radio("Login with", ["Email", "Mobile Number"], horizontal=True)

    with st.form("login_form"):
        if login_method == "Email":
            identifier = st.text_input("Email")
        else:
            identifier = st.text_input(
                "Mobile Number", placeholder="+91XXXXXXXXXX (include country code)"
            )
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if login_method == "Email":
                login_with_email(identifier, password)
            else:
                login_with_phone(identifier, password)

    st.caption(
        "Students/parents: use the mobile number and password your coaching "
        "center gave you. Admin/teachers: use your email."
    )
else:
    st.success(f"Logged in as {st.session_state.full_name} ({st.session_state.role})")
    st.write("Use the sidebar on the left to open your dashboard.")
    if st.button("Logout"):
        logout()
