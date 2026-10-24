import streamlit as st

st.set_page_config(
    page_title="MindSeek",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from utils.db import init_db, get_or_create_user
from utils.ui_helpers import load_css, ensure_session

# Auto-initialize SQLite database on first launch
init_db()
ensure_session()
load_css()

# Hide Streamlit Chrome Elements
st.markdown("""<style>
#MainMenu {visibility: hidden; display: none !important;}
footer {visibility: hidden; display: none !important;}
header [data-testid="stToolbar"] {visibility: hidden; display: none !important;}
header button[kind="header"] {display: none !important;}
div[data-testid="stDeployButton"] {display: none !important;}
[data-testid="stDecoration"] {visibility: hidden; display: none !important;}
header[data-testid="stHeader"] {background: transparent !important;}
[data-testid="InputInstructions"] {display: none !important;}
</style>""", unsafe_allow_html=True)

# Main Container with 2-Column Academic Layout
st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

col_left, col_right = st.columns([1.2, 1], gap="large")

with col_left:
    left_panel_html = """<div style="background: linear-gradient(145deg, #F0F9F9 0%, #E6F4F4 50%, #DCF0F0 100%); border: 1px solid #CCECEC; border-radius: 16px; padding: 44px 38px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); position: relative; overflow: hidden;">
<div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background-image: radial-gradient(#0E8A8A 1px, transparent 1px); background-size: 24px 24px; opacity: 0.12; pointer-events: none;"></div>
<div style="position: relative; z-index: 1;">
<div style="width: 56px; height: 56px; background: #0E8A8A; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 28px; color: #FFFFFF; box-shadow: 0 4px 12px rgba(14, 138, 138, 0.28); margin-bottom: 20px;">
🔍
</div>
<h1 style="font-size: 2.4rem; margin: 0 0 8px 0; color: #111827; font-family: 'Merriweather', serif; font-weight: 700;">
MindSeek
</h1>
<p style="font-family: 'Merriweather', serif; font-style: italic; color: #0E8A8A; font-size: 1.15rem; margin: 0 0 18px 0; font-weight: 400;">
"Seek the Mind of Every Paper"
</p>
<p style="font-size: 0.95rem; color: #4B5563; line-height: 1.6; margin-bottom: 30px;">
Automated research paper comparator for rapid methodology extraction, dataset benchmarking, and synthesis across research papers.
</p>
<div style="display: flex; flex-direction: column; gap: 14px;">
<div style="display: flex; align-items: center; gap: 14px; background: rgba(255, 255, 255, 0.88); border: 1px solid rgba(209, 236, 236, 0.85); border-radius: 12px; padding: 14px 18px; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
<div style="width: 38px; height: 38px; border-radius: 10px; background: #E6F4F4; display: flex; align-items: center; justify-content: center; font-size: 18px; color: #0E8A8A;">
📄
</div>
<div>
<div style="font-weight: 600; font-size: 0.92rem; color: #111827;">Research Papers</div>
<div style="font-size: 0.8rem; color: #6B7280;">High-speed 2-column PDF decomposition</div>
</div>
</div>
<div style="display: flex; align-items: center; gap: 14px; background: rgba(255, 255, 255, 0.88); border: 1px solid rgba(209, 236, 236, 0.85); border-radius: 12px; padding: 14px 18px; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
<div style="width: 38px; height: 38px; border-radius: 10px; background: #E6F4F4; display: flex; align-items: center; justify-content: center; font-size: 18px; color: #0E8A8A;">
⚡
</div>
<div>
<div style="font-weight: 600; font-size: 0.92rem; color: #111827;">AI-Powered</div>
<div style="font-size: 0.8rem; color: #6B7280;">Instant methodology & benchmark extraction</div>
</div>
</div>
<div style="display: flex; align-items: center; gap: 14px; background: rgba(255, 255, 255, 0.88); border: 1px solid rgba(209, 236, 236, 0.85); border-radius: 12px; padding: 14px 18px; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
<div style="width: 38px; height: 38px; border-radius: 10px; background: #E6F4F4; display: flex; align-items: center; justify-content: center; font-size: 18px; color: #0E8A8A;">
🔒
</div>
<div>
<div style="font-weight: 600; font-size: 0.92rem; color: #111827;">Secure Access</div>
<div style="font-size: 0.8rem; color: #6B7280;">Personal researcher archive & session history</div>
</div>
</div>
</div>
</div>
</div>"""
    st.markdown(left_panel_html, unsafe_allow_html=True)

with col_right:
    right_box_open = """<div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); padding: 42px 36px;">
<div style="margin-bottom: 22px;">
<h3 style="margin-bottom: 6px; font-size: 1.45rem; color: #111827;">Researcher Login</h3>
<p style="font-size: 0.88rem; color: #6B7280; margin: 0;">Enter your academic credentials to access the archive.</p>
</div>"""
    st.markdown(right_box_open, unsafe_allow_html=True)

    if st.session_state.get("user_id"):
        st.info(f"Active Session: **{st.session_state.get('user_name')}** ({st.session_state.get('user_email')})")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Continue to Archive ➔", use_container_width=True):
                st.switch_page("pages/1_Home_Upload.py")
        with c2:
            if st.button("Switch Account", use_container_width=True):
                st.session_state.user_id = None
                st.session_state.user_name = None
                st.session_state.user_email = None
                st.rerun()
    else:
        with st.form("researcher_login_form"):
            name = st.text_input("Full Name", placeholder="Enter your full name")
            email = st.text_input("Academic / Work Email", placeholder="you@university.edu")
            
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Enter Archive ➔", use_container_width=True)

            if submitted:
                if not name.strip() or not email.strip():
                    st.error("Please enter both your name and academic email address.")
                elif "@" not in email or "." not in email:
                    st.error("Please enter a valid email format.")
                else:
                    user = get_or_create_user(name=name.strip(), email=email.strip())
                    st.session_state.user_id = user["id"]
                    st.session_state.user_name = user["name"]
                    st.session_state.user_email = user["email"]
                    st.switch_page("pages/1_Home_Upload.py")

    st.markdown("</div>", unsafe_allow_html=True)
