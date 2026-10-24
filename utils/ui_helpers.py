import os
import streamlit as st

def load_css():
    """Injects the custom paper desk CSS stylesheet into the Streamlit app."""
    css_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

def ensure_session():
    """Ensures user session variables exist and user is logged in where required."""
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "user_name" not in st.session_state:
        st.session_state.user_name = None
    if "user_email" not in st.session_state:
        st.session_state.user_email = None
    if "current_paper_id" not in st.session_state:
        st.session_state.current_paper_id = None
    if "compare_paper_ids" not in st.session_state:
        st.session_state.compare_paper_ids = []

def require_login():
    """Redirects to landing / login page if user is not authenticated."""
    ensure_session()
    if not st.session_state.user_id:
        st.warning("Please sign in with your researcher credentials to access this archive section.")
        if st.button("Go to Login"):
            st.switch_page("app.py")
        st.stop()
