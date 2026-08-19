import streamlit as st
from supabase import create_client, Client


@st.cache_resource
def init_supabase_admin() -> Client:
    """A second, more powerful connection to Supabase — used ONLY for admin
    actions like creating teacher/parent logins. Never expose this key to
    the browser; it only ever runs here on the server side.
    """
    url = st.secrets["SUPABASE_URL"]
    service_key = st.secrets["SUPABASE_SERVICE_KEY"]
    return create_client(url, service_key)


supabase_admin = init_supabase_admin()
