import streamlit as st
st.set_page_config(page_title="MindSeek - Prism", page_icon="🔍", layout="wide", initial_sidebar_state="collapsed")
import os, sys
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path: sys.path.insert(0, BASE_DIR)
from utils.db import init_db, get_or_create_user
from utils.ui_helpers import load_css, ensure_session

init_db()
ensure_session()
load_css()

st.markdown("""
<style>
#MainMenu, footer, header [data-testid="stToolbar"], header button[kind="header"], div[data-testid="stDeployButton"] {display:none !important;}
.stApp {background: #f7fdfc !important;}
.left-card { background: linear-gradient(165deg, #f0fdfa 0%, #e6fffa 100%); border: 1px solid #c6ecec; border-radius: 16px; padding: 32px 30px; }
.logo { width: 52px; height: 52px; background: #0E8A8A; border-radius: 12px; display:flex; align-items:center; justify-content:center; font-size:24px; color:white; }
.item { display:flex; gap:12px; background: rgba(255,255,255,0.9); border: 1px solid #e6f4f4; border-radius: 10px; padding: 12px 14px; margin-bottom: 10px; }
div[data-testid="stForm"] { background: white !important; border: 1px solid #e5e7eb !important; border-radius: 16px !important; padding: 28px !important; box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important; }
div[data-testid="stTextInput"] input { border-radius: 10px !important; }
div[data-testid="stFormSubmitButton"] button { background: #0E8A8A !important; color: white !important; border-radius: 10px !important; border: none !important; }
</style>
""", unsafe_allow_html=True)

col_left, col_right = st.columns([1.2, 1], gap="large")

with col_left:
    st.markdown("""
    <div class="left-card">
        <div class="logo">🔍</div>
        <h1 style="font-size:2.2rem; margin:12px 0 6px 0; color:#111827; font-weight:700;">MindSeek</h1>
        <p style="font-style:italic; color:#0E8A8A; font-size:1.05rem; margin:0 0 10px 0;">"Seek the Mind of Every Paper"</p>
        <p style="font-size:0.9rem; color:#4B5563; line-height:1.5; margin-bottom:20px;">Automated research paper comparator for rapid methodology extraction, dataset benchmarking, and synthesis across research papers.</p>
        <div class="item"><div>📄</div><div><div style="font-weight:600; font-size:0.9rem;">Research Papers</div><div style="font-size:0.78rem; color:#6B7280;">High-speed 2-column PDF decomposition</div></div></div>
        <div class="item"><div>⚡</div><div><div style="font-weight:600; font-size:0.9rem;">AI-Powered</div><div style="font-size:0.78rem; color:#6B7280;">Instant methodology & benchmark extraction</div></div></div>
        <div class="item"><div>🔒</div><div><div style="font-weight:600; font-size:0.9rem;">Secure Access</div><div style="font-size:0.78rem; color:#6B7280;">Personal researcher archive & session history</div></div></div>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    with st.form("login"):
        st.markdown("### Researcher Login")
        st.markdown("<p style='font-size:0.85rem; color:#6B7280; margin-top:-10px; margin-bottom:20px;'>Enter your academic credentials to access the archive.</p>", unsafe_allow_html=True)
        name = st.text_input("Full Name", placeholder="Dr. Keerthana B")
        email = st.text_input("Academic / Work Email", placeholder="you@university.edu")
        ok = st.form_submit_button("Enter Archive →", use_container_width=True)
        if ok:
            if not name.strip() or "@" not in email:
                st.error("Enter valid name and email")
            else:
                user = get_or_create_user(name=name.strip(), email=email.strip())
                st.session_state.user_id = user["id"]
                st.session_state.user_name = user["name"]
                st.session_state.user_email = user["email"]
                st.switch_page("pages/1_Home_Upload.py")