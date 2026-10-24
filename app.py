import streamlit as st

st.set_page_config(
    page_title="MindSeek - Prism",
    page_icon="🔍",
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

init_db()
ensure_session()
load_css()

# --- PREMIUM LOGIN CSS - ONLY FOR THIS PAGE ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;700&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap');

#MainMenu, footer, header [data-testid="stToolbar"], header button[kind="header"], div[data-testid="stDeployButton"], [data-testid="stDecoration"] {display:none !important;}
header[data-testid="stHeader"] {background: transparent !important;}

.stApp {
    background: radial-gradient(900px at 15% 20%, #e0fdfa 0%, transparent 50%),
                radial-gradient(800px at 85% 80%, #ccfbf1 0%, transparent 50%),
                #f8fafc !important;
}

/* Left Premium Panel */
.left-premium {
    background: linear-gradient(165deg, #f0fdfa 0%, #ecfeff 30%, #d9f9f5 100%);
    border: 1px solid #b8e6e6;
    border-radius: 20px;
    padding: 44px 38px;
    box-shadow: 0 8px 32px rgba(14,138,138,0.08), inset 0 1px 0 rgba(255,255,255,0.8);
    position: relative;
    overflow: hidden;
    min-height: 580px;
}
.left-premium::before {
    content:'';
    position:absolute;
    width:500px; height:500px;
    background: radial-gradient(circle, rgba(20,184,166,0.12) 0%, transparent 70%);
    top:-150px; left:-120px;
}

/* Right Premium Panel */
.right-premium {
    background: rgba(255,255,255,0.92);
    backdrop-filter: blur(12px);
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 44px 38px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.06);
    min-height: 580px;
}

.logo-box {
    width: 58px; height: 58px;
    background: linear-gradient(135deg, #0e8a8a 0%, #14b8a6 100%);
    border-radius: 16px;
    display:flex; align-items:center; justify-content:center;
    font-size:28px; color:white;
    box-shadow: 0 8px 20px rgba(14,138,138,0.32);
    position:relative; z-index:2;
}

.feat-card {
    display:flex; align-items:center; gap:14px;
    background: rgba(255,255,255,0.9);
    border: 1px solid #e6f4f4;
    border-radius: 14px;
    padding: 14px 18px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    transition: all 0.25s ease;
}
.feat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    border-color: #b8e6e6;
}

/* Inputs */
div[data-testid="stTextInput"] input {
    border-radius: 12px !important;
    border: 1.5px solid #e2e8f0 !important;
    padding: 13px 16px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    transition: all 0.2s !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #14b8a6 !important;
    box-shadow: 0 0 0 3px rgba(20,184,166,0.15) !important;
}

/* Buttons */
div[data-testid="stFormSubmitButton"] button, div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #0e8a8a 0%, #14b8a6 100%) !important;
    color: white !important;
    border-radius: 12px !important;
    padding: 13px !important;
    font-weight: 600 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    border: none !important;
    box-shadow: 0 4px 16px rgba(14,138,138,0.32) !important;
    transition: all 0.2s !important;
}
div[data-testid="stFormSubmitButton"] button:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 24px rgba(14,138,138,0.42) !important;
}

label { font-family: 'Plus Jakarta Sans', sans-serif !important; font-weight: 500 !important; font-size: 13.5px !important; color: #334155 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

col_left, col_right = st.columns([1.2, 1], gap="large")

with col_left:
    st.markdown(f"""
    <div class="left-premium">
        <div style="position:relative; z-index:2;">
            <div class="logo-box">🔍</div>
            <h1 style="font-family:'Outfit', sans-serif; font-size:2.6rem; margin:18px 0 6px 0; color:#0f172a; font-weight:700; letter-spacing:-0.8px;">MindSeek</h1>
            <p style="font-family:'Outfit', sans-serif; font-style:italic; color:#0e8a8a; font-size:1.15rem; margin:0 0 16px 0; font-weight:500;">"Seek the Mind of Every Paper"</p>
            <p style="font-family:'Plus Jakarta Sans', sans-serif; font-size:0.95rem; color:#475569; line-height:1.6; margin-bottom:28px;">
                Automated research paper comparator for rapid methodology extraction, dataset benchmarking, and synthesis across research papers.
            </p>
            <div style="display:flex; flex-direction:column; gap:12px;">
                <div class="feat-card">
                    <div style="width:38px; height:38px; border-radius:10px; background:#e6f8f7; display:flex; align-items:center; justify-content:center; font-size:18px;">📄</div>
                    <div><div style="font-weight:600; font-size:0.92rem; color:#0f172a; font-family:'Plus Jakarta Sans';">Research Papers</div><div style="font-size:0.8rem; color:#64748b; font-family:'Plus Jakarta Sans';">High-speed 2-column PDF decomposition</div></div>
                </div>
                <div class="feat-card">
                    <div style="width:38px; height:38px; border-radius:10px; background:#fef9c3; display:flex; align-items:center; justify-content:center; font-size:18px;">⚡</div>
                    <div><div style="font-weight:600; font-size:0.92rem; color:#0f172a; font-family:'Plus Jakarta Sans';">AI-Powered</div><div style="font-size:0.8rem; color:#64748b; font-family:'Plus Jakarta Sans';">Instant methodology & benchmark extraction</div></div>
                </div>
                <div class="feat-card">
                    <div style="width:38px; height:38px; border-radius:10px; background:#ffedd5; display:flex; align-items:center; justify-content:center; font-size:18px;">🔒</div>
                    <div><div style="font-weight:600; font-size:0.92rem; color:#0f172a; font-family:'Plus Jakarta Sans';">Secure Access</div><div style="font-size:0.8rem; color:#64748b; font-family:'Plus Jakarta Sans';">Personal researcher archive & session history</div></div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown("""
    <div class="right-premium">
        <div style="margin-bottom: 10px;">
            <h3 style="font-family:'Outfit', sans-serif; font-size:1.5rem; color:#0f172a; margin:0 0 6px 0; font-weight:700;">Researcher Login</h3>
            <p style="font-family:'Plus Jakarta Sans', sans-serif; font-size:0.88rem; color:#64748b; margin:0;">Enter your academic credentials to access the archive.</p>
        </div>
    """, unsafe_allow_html=True)

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
            name = st.text_input("Full Name", placeholder="Dr. Keerthana B")
            email = st.text_input("Academic / Work Email", placeholder="you@university.edu")
            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
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