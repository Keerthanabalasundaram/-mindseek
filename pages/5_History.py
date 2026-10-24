import streamlit as st
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from utils.db import get_user_papers, get_user_comparisons, get_papers_by_ids
from utils.report_generator import generate_single_paper_pdf, generate_comparison_pdf
from utils.ui_helpers import load_css, require_login

st.set_page_config(
    page_title="MindSeek | My History",
    page_icon="🏛️",
    layout="wide"
)

require_login()
load_css()

user_id = st.session_state.get("user_id")
user_name = st.session_state.get("user_name", "Researcher")

col_head_l, col_head_r = st.columns([3, 1])
with col_head_l:
    st.markdown("""<h2 style="margin-top: 4px; margin-bottom: 2px;">My History</h2>
<p style="color: #666666; font-size: 0.95rem; margin-top: 0;">
Review past research paper extractions and retrieve comparative reports.
</p>""", unsafe_allow_html=True)

with col_head_r:
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    if st.button("➕ Upload New Paper", use_container_width=True):
        st.switch_page("pages/1_Home_Upload.py")

st.markdown("<hr>", unsafe_allow_html=True)

# Fetch user history safely handling None always
papers = get_user_papers(user_id) or []
comparisons = get_user_comparisons(user_id) or []

tab1, tab2 = st.tabs([f"Analyzed Papers ({len(papers)})", f"Paper Comparisons ({len(comparisons)})"])

# Tab 1: Analyzed Papers
with tab1:
    if not papers:
        st.info("You haven't uploaded any research papers yet. Upload your first PDF to begin building your archive.")
        if st.button("Upload Research Paper ➔"):
            st.switch_page("pages/1_Home_Upload.py")
    else:
        st.markdown(f"<div style='font-size: 0.9rem; color: #666666; margin-bottom: 14px;'>Total Analyzed: <strong>{len(papers)} papers</strong></div>", unsafe_allow_html=True)

        for p in papers:
            if not p:
                continue
            acc = float(p.get("accuracy", 0.0) or 0.0)
            m_val = p.get('methodology') or 'Not specified'
            if m_val.lower() == 'signing':
                m_val = 'Transformer'

            col_info, col_actions = st.columns([3.5, 1.5])

            with col_info:
                p_title = p.get('filename') or 'Untitled'
                p_id = p.get('id', 0)
                p_date = p.get('created_at', '')
                p_dataset = p.get('dataset', 'Benchmark Dataset')

                html_card = f"""<div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-left: 4px solid #0E8A8A; border-radius: 16px; padding: 16px 20px; margin-bottom: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
<div style="display: flex; justify-content: space-between; align-items: baseline;">
<span style="font-weight: 700; font-size: 1.05rem; color: #1A1A1A;">📄 {p_title}</span>
<span style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #888888;">#{p_id} &bull; {p_date}</span>
</div>
<div style="display: flex; gap: 24px; margin-top: 8px; font-size: 0.88rem;">
<span><strong>Methodology:</strong> <span style="color: #0E8A8A; font-weight: 600;">{m_val}</span></span>
<span><strong>Dataset:</strong> {p_dataset}</span>
<span><strong>Accuracy:</strong> <span style="font-weight: 700; color: #0E8A8A;">{acc:.1f}%</span></span>
</div>
</div>"""
                st.markdown(html_card, unsafe_allow_html=True)

            with col_actions:
                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("View Result", key=f"view_p_{p['id']}", use_container_width=True):
                        st.session_state.current_paper_id = p["id"]
                        st.switch_page("pages/2_Single_Result.py")
                with b2:
                    single_pdf = generate_single_paper_pdf(p, user_name=user_name)
                    with open(single_pdf, "rb") as sf:
                        s_bytes = sf.read()
                    st.download_button(
                        label="PDF 📥",
                        data=s_bytes,
                        file_name=f"MindSeek_Paper_{p['id']}.pdf",
                        mime="application/pdf",
                        key=f"dl_p_{p['id']}",
                        use_container_width=True
                    )

# Tab 2: Comparisons
with tab2:
    if not comparisons:
        st.info("No comparative evaluations generated yet. Select 2 or more papers to perform cross-paper benchmarking.")
        if st.button("Start Paper Comparison ➔"):
            st.switch_page("pages/3_Compare.py")
    else:
        st.markdown(f"<div style='font-size: 0.9rem; color: #666666; margin-bottom: 14px;'>Comparative Reports: <strong>{len(comparisons)} sessions</strong></div>", unsafe_allow_html=True)

        for comp in comparisons:
            if not comp:
                continue
            raw_ids = comp.get("paper_ids", "")
            try:
                p_ids = [int(x.strip()) for x in raw_ids.split(",") if x.strip()]
            except Exception:
                p_ids = []

            comp_papers = get_papers_by_ids(p_ids) or []
            paper_titles = ", ".join([p.get("filename", "") for p in comp_papers]) if comp_papers else f"Papers {raw_ids}"

            col_c_info, col_c_act = st.columns([3.5, 1.5])
            with col_c_info:
                comp_id = comp.get('id', 0)
                comp_date = comp.get('created_at', '')
                html_comp_card = f"""<div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-left: 4px solid #0E8A8A; border-radius: 16px; padding: 16px 20px; margin-bottom: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
<div style="display: flex; justify-content: space-between; align-items: baseline;">
<span style="font-weight: 700; font-size: 1.05rem; color: #1A1A1A;">📊 Comparison #{comp_id} ({len(p_ids)} Papers)</span>
<span style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #888888;">{comp_date}</span>
</div>
<div style="font-size: 0.85rem; color: #555555; margin-top: 6px;">
<strong>Evaluated Papers:</strong> {paper_titles}
</div>
</div>"""
                st.markdown(html_comp_card, unsafe_allow_html=True)

            with col_c_act:
                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                cb1, cb2 = st.columns(2)
                with cb1:
                    if st.button("Reopen", key=f"reopen_{comp['id']}", use_container_width=True):
                        st.session_state.compare_paper_ids = p_ids
                        st.switch_page("pages/4_Comparison_Dashboard.py")
                with cb2:
                    rep_path = comp.get("report_path")
                    if rep_path and os.path.exists(rep_path):
                        with open(rep_path, "rb") as cf:
                            c_bytes = cf.read()
                    else:
                        rec = {
                            "blueprint": "Combine the top methodology with the richest dataset to achieve peak accuracy.",
                            "best_methodology": comp_papers[0].get("methodology") if comp_papers else "Transformer",
                            "best_dataset": comp_papers[0].get("dataset") if comp_papers else "MS COCO"
                        }
                        new_rep = generate_comparison_pdf(comp_papers, rec, user_name=user_name)
                        with open(new_rep, "rb") as cf:
                            c_bytes = cf.read()

                    st.download_button(
                        label="Report 📥",
                        data=c_bytes,
                        file_name=f"MindSeek_Comparison_{comp['id']}.pdf",
                        mime="application/pdf",
                        key=f"dl_c_{comp['id']}",
                        use_container_width=True
                    )
