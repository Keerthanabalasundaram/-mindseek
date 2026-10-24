import streamlit as st
import os
import sys
import tempfile
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from utils.db import save_paper, get_user_papers, find_cached_paper
from utils.docling_extractor import extract_text_from_pdf
from utils.section_cutter import cut_methodology_section
from utils.scispacy_extractor import extract_entities
from utils.accuracy_extractor import extract_accuracy
from utils.github_api import search_github_repos
from utils.ui_helpers import load_css, require_login

st.set_page_config(
    page_title="MindSeek | Compare Research Papers",
    page_icon="📑",
    layout="wide"
)

require_login()
load_css()

st.markdown("""<div style="margin-bottom: 8px;">
<h2 style="margin-top: 4px; margin-bottom: 2px;">Compare Research Papers</h2>
<p style="color: #666666; font-size: 0.95rem; margin-top: 0;">
Select up to 10 research papers for side-by-side methodology analysis and comparative benchmarking.
</p>
</div>
<hr>""", unsafe_allow_html=True)

col_upload, col_existing = st.columns([1.5, 1.2], gap="large")

with col_upload:
    st.markdown("### 1. Upload Additional Research Papers (Up to 10)")
    st.markdown("""<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
<span style="font-size: 1.2rem;">📎</span>
<span style="font-weight: 500; font-size: 0.95rem; color: #333333;">Select research papers to compare</span>
</div>""", unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Upload multiple PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload research papers to compare",
        label_visibility="collapsed"
    )

    if uploaded_files:
        if len(uploaded_files) > 10:
            st.warning("Maximum of 10 papers supported at once. The first 10 will be processed.")
            uploaded_files = uploaded_files[:10]

        st.markdown(f"**Selected Papers ({len(uploaded_files)} files):**")
        
        for idx, f in enumerate(uploaded_files):
            kb = len(f.getvalue()) / 1024
            card_html = f"""<div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-left: 4px solid #0E8A8A; border-radius: 16px; padding: 14px 18px; margin-bottom: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
<div style="display: flex; justify-content: space-between; align-items: center;">
<span style="font-weight: 600; font-size: 0.9rem; color: #1A1A1A;">[{idx+1}] 📄 {f.name}</span>
<span style="font-size: 0.78rem; color: #888888; font-family: 'JetBrains Mono', monospace;">{kb:.1f} KB &bull; Queued</span>
</div>
</div>"""
            st.markdown(card_html, unsafe_allow_html=True)

with col_existing:
    st.markdown("### 2. Include Previously Analyzed Papers")
    st.markdown("<p style='font-size: 0.88rem; color: #666666;'>Select papers already indexed in your personal archive:</p>", unsafe_allow_html=True)
    
    user_papers = get_user_papers(st.session_state.user_id) or []
    selected_existing_ids = []

    if user_papers:
        default_checked_ids = st.session_state.get("compare_paper_ids", [])

        for p in user_papers:
            if not p:
                continue
            is_checked = p["id"] in default_checked_ids
            method_display = p.get('methodology') or 'Not specified'
            if method_display.lower() == 'signing':
                method_display = 'Transformer'

            check_label = f"#{p['id']} - {p.get('filename', 'Untitled')} ({method_display} | {p.get('accuracy', 0):.1f}%)"
            if st.checkbox(check_label, value=is_checked, key=f"exist_p_{p['id']}"):
                selected_existing_ids.append(p["id"])
    else:
        st.info("No past papers found in your archive. Upload new papers on the left to begin.")

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

total_count = len(uploaded_files if uploaded_files else []) + len(selected_existing_ids)

if total_count == 0:
    st.info("Please upload or select at least 2 research papers to perform comparative analysis.")
elif total_count == 1:
    st.info(f"You have selected 1 paper. Select or upload at least one more paper to unlock cross-paper comparison (Total: {total_count}/10).")

col_sub_l, col_sub_r = st.columns([2, 1])
with col_sub_l:
    submit_compare = st.button(
        f"🚀 Compare Selected Papers ({total_count} papers) ➔",
        disabled=(total_count < 2),
        use_container_width=True
    )

if submit_compare and total_count >= 2:
    all_final_ids = list(selected_existing_ids)
    progress_bar = st.progress(0.1)
    status_text = st.empty()

    if uploaded_files:
        for idx, f in enumerate(uploaded_files, 1):
            status_text.markdown(f"<span style='color: #0E8A8A;'>Processing paper [{idx}/{len(uploaded_files)}]: {f.name}...</span>", unsafe_allow_html=True)
            progress_bar.progress(0.1 + (idx / len(uploaded_files)) * 0.8)

            cached = find_cached_paper(st.session_state.user_id, f.name)
            if cached:
                all_final_ids.append(cached["id"])
            else:
                temp_dir = tempfile.gettempdir()
                temp_pdf = os.path.join(temp_dir, f"comp_{idx}_{int(time.time())}_{f.name}")
                with open(temp_pdf, "wb") as out_f:
                    out_f.write(f.getbuffer())

                full_text, _ = extract_text_from_pdf(temp_pdf)
                method_text, _ = cut_methodology_section(full_text)
                entities = extract_entities(method_text, full_text)
                acc_val, _, _ = extract_accuracy(method_text, full_text)
                repos = search_github_repos(entities["methodology"])

                pid = save_paper(
                    user_id=st.session_state.user_id,
                    filename=f.name,
                    methodology=entities["methodology"],
                    dataset=entities["dataset"],
                    accuracy=acc_val,
                    extracted_text=method_text[:8000],
                    github_repos=repos
                )
                all_final_ids.append(pid)

                try:
                    if os.path.exists(temp_pdf):
                        os.remove(temp_pdf)
                except Exception:
                    pass

    unique_ids = []
    for pid in all_final_ids:
        if pid not in unique_ids:
            unique_ids.append(pid)

    st.session_state.compare_paper_ids = unique_ids
    progress_bar.progress(1.0)
    status_text.success("All papers successfully extracted! Opening Paper Comparison...")
    time.sleep(0.3)
    st.switch_page("pages/4_Comparison_Dashboard.py")
