import streamlit as st
from utils.supabase_client import supabase
from utils.branding import show_header

st.set_page_config(page_title="Shivam Classes ERP", page_icon="utils/logo.jpg")

# Keep track of who is logged in across page switches
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.role = None
    st.session_state.full_name = None


def login(email: str, password: str):
    try:
        result = supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
        user = result.user

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
    except Exception as e:
        st.error(f"Login failed: {e}")


def logout():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.session_state.role = None
    st.session_state.full_name = None
    st.rerun()


show_header()

if st.session_state.user is None:
    st.subheader("Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            login(email, password)

    st.caption(
        "No account yet? Create users from the Supabase dashboard "
        "(Authentication tab) for now — a self-signup form can be added later."
    )
else:
    st.success(f"Logged in as {st.session_state.full_name} ({st.session_state.role})")
    st.write("Use the sidebar on the left to open your dashboard.")
    if st.button("Logout"):
        logout()
