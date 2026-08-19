import base64
import os
import streamlit as st

_LOGO_PATH = os.path.join(os.path.dirname(__file__), "logo.jpg")


@st.cache_data
def _get_logo_base64() -> str:
    with open(_LOGO_PATH, "rb") as f:
        return base64.b64encode(f.read()).decode()


def show_header(subtitle: str = ""):
    """Renders the Shivam Classes navy-and-gold header banner with the real
    logo. Call this at the top of every page instead of st.title(...).
    """
    logo_b64 = _get_logo_base64()

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #0D1B2A 0%, #1B2A41 100%);
            padding: 24px 28px;
            border-radius: 12px;
            border-left: 6px solid #D4A017;
            margin-bottom: 24px;
        ">
            <div style="display:flex; align-items:center; gap:14px;">
                <img src="data:image/jpeg;base64,{logo_b64}" style="
                    width:52px; height:52px; border-radius:50%;
                    object-fit:cover; border:2px solid #D4A017;
                    flex-shrink:0;
                " />
                <div>
                    <div style="font-size:26px; font-weight:800; color:#FFFFFF; letter-spacing:1px; line-height:1.2;">
                        SHIVAM CLASSES
                    </div>
                    <div style="font-size:12px; color:#D4A017; letter-spacing:1.5px; text-transform:uppercase; margin-top:2px;">
                        Coaching for Success &middot; Classes 5th&ndash;12th (All Boards)
                    </div>
                </div>
            </div>
            {f'<div style="margin-top:14px; font-size:19px; color:#FFFFFF; font-weight:600;">{subtitle}</div>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )
