import streamlit as st
from supabase import create_client, Client


@st.cache_resource
def init_supabase() -> Client:
    """Creates one shared connection to your Supabase project.
    Reads the URL and key from .streamlit/secrets.toml
    """
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


supabase = init_supabase()
