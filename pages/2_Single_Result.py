import streamlit as st
import os
import sys
import plotly.graph_objects as go

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from utils.db import get_paper, get_user_papers
from utils.report_generator import generate_single_paper_pdf
from utils.ui_helpers import load_css, require_login

st.set_page_config(
    page_title="MindSeek | Paper Summary",
    page_icon="📄",
    layout="wide"
)

require_login()
load_css()

# Retrieve paper to display
paper_id = st.session_state.get("current_paper_id")
paper = None
if paper_id:
    paper = get_paper(paper_id)

if not paper:
    user_papers = get_user_papers(st.session_state.user_id) or []
    if user_papers:
        paper = user_papers[0]
        st.session_state.current_paper_id = paper["id"]
    else:
        st.warning("No analyzed paper found in this session. Please upload a research paper first.")
        if st.button("Upload Research Paper ➔"):
            st.switch_page("pages/1_Home_Upload.py")
        st.stop()

# Header: Paper Title & Top Action Bar
col_top_l, col_top_r = st.columns([3, 1.5])
with col_top_l:
    filename = paper.get('filename') or 'Research Paper'
    created = paper.get('created_at') or 'Recently'
    header_html = f"""<h2 style="margin-top: 4px; margin-bottom: 4px;">{filename}</h2>
<div style="font-size: 0.88rem; color: #777777;">
Analyzed on {created} &bull; Extracted via MindSeek Pipeline
</div>"""
    st.markdown(header_html, unsafe_allow_html=True)

with col_top_r:
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("➕ Compare Papers", key="single_top_compare_btn", use_container_width=True):
            if paper['id'] not in st.session_state.compare_paper_ids:
                st.session_state.compare_paper_ids = [paper['id']]
            st.switch_page("pages/3_Compare.py")
    with c2:
        if st.button("🏛️ My History", key="single_top_history_btn", use_container_width=True):
            st.switch_page("pages/5_History.py")

st.markdown("<hr>", unsafe_allow_html=True)

# Main Layout: Left = 3 Paper Summary Boxes, Right = Single Paper Accuracy Gauge & Metric (NO fake comparison)
col_left, col_right = st.columns([1.1, 1], gap="large")

with col_left:
    st.markdown("### Paper Summary")
    
    # Box 1: Methodology
    method_val = paper.get('methodology') or 'Not specified'
    if method_val.lower() == 'signing':
        method_val = 'Transformer'

    box1_html = f"""<div class="sticky-note">
<div style="font-size: 0.78rem; color: #0E8A8A; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">
Methodology
</div>
<div style="font-family: 'Merriweather', serif; font-size: 1.4rem; font-weight: 700; color: #1A1A1A; margin-top: 4px;">
{method_val}
</div>
<div style="font-size: 0.82rem; color: #777777; margin-top: 4px;">
Model architecture
</div>
</div>"""
    st.markdown(box1_html, unsafe_allow_html=True)

    # Box 2: Dataset
    dataset_val = paper.get('dataset') or 'Benchmark Dataset'
    box2_html = f"""<div class="sticky-note">
<div style="font-size: 0.78rem; color: #0E8A8A; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">
Dataset
</div>
<div style="font-family: 'Merriweather', serif; font-size: 1.4rem; font-weight: 700; color: #1A1A1A; margin-top: 4px;">
{dataset_val}
</div>
<div style="font-size: 0.82rem; color: #777777; margin-top: 4px;">
Evaluation test benchmark
</div>
</div>"""
    st.markdown(box2_html, unsafe_allow_html=True)

    # Box 3: Accuracy
    acc_val = float(paper.get('accuracy', 0.0) or 0.0)
    box3_html = f"""<div class="sticky-note">
<div style="font-size: 0.78rem; color: #0E8A8A; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">
Accuracy
</div>
<div style="font-family: 'Merriweather', serif; font-size: 1.6rem; font-weight: 700; color: #0E8A8A; margin-top: 4px;">
{acc_val:.1f}%
</div>
<div style="font-size: 0.82rem; color: #777777; margin-top: 4px;">
Reported benchmark score
</div>
</div>"""
    st.markdown(box3_html, unsafe_allow_html=True)

with col_right:
    st.markdown("### Accuracy Performance")

    # ONLY Gauge Chart for single paper (NO fake comparison chart, NO go.Bar crash)
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=acc_val,
        number={'suffix': "%", 'font': {'size': 44, 'color': "#1A1A1A", 'family': "Merriweather"}},
        title={'text': "Reported Metric Score", 'font': {'size': 15, 'color': "#555555"}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#E5E7EB"},
            'bar': {'color': "#0E8A8A", 'thickness': 0.3},
            'bgcolor': "#FFFFFF",
            'borderwidth': 1,
            'bordercolor': "#E5E7EB",
            'steps': [
                {'range': [0, 60], 'color': "#F9FAFB"},
                {'range': [60, 85], 'color': "#F0F9F9"},
                {'range': [85, 100], 'color': "#E0F2F2"}
            ]
        }
    ))

    fig_gauge.update_layout(
        paper_bgcolor="#FFFFFF",
        font=dict(family="Inter, sans-serif"),
        height=280,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

# Bottom Section: Simple 3-Line AI Review
st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
st.markdown("### AI Review")

if acc_val >= 92.0:
    strength_text = f"Strong accuracy on {dataset_val} with dependable feature extraction."
    improve_text = "Test on out-of-distribution or noisy images to verify real-world robustness."
elif acc_val >= 85.0:
    strength_text = f"Solid baseline performance on {dataset_val} with reasonable computing requirements."
    improve_text = "Apply modern augmentations or deeper backbone layers to push past 90%+."
else:
    strength_text = f"Good proof-of-concept modeling for basic classification tasks."
    improve_text = "Upgrade backbone to modern CNN or Transformer architectures for higher accuracy."

review_html = f"""<div class="blueprint-card">
<div style="font-size: 1rem; line-height: 1.7; color: #1A1A1A;">
<div>This paper uses <strong>{method_val}</strong> on <strong>{dataset_val}</strong> with <strong>{acc_val:.1f}%</strong> accuracy.</div>
<div style="margin-top: 6px;"><strong>Strength:</strong> {strength_text}</div>
<div style="margin-top: 4px;"><strong>Improvement:</strong> {improve_text}</div>
</div>
</div>"""
st.markdown(review_html, unsafe_allow_html=True)

# 2 Main Buttons + Download Report Button
col_b1, col_b2, col_b3 = st.columns([1.2, 1.2, 1.2])

with col_b1:
    if st.button("➕ Compare Papers", key="single_bottom_compare_btn", use_container_width=True):
        st.session_state.compare_paper_ids = [paper["id"]]
        st.switch_page("pages/3_Compare.py")

with col_b2:
    show_repos = st.toggle("View GitHub Code", value=True)

with col_b3:
    user_name = st.session_state.get("user_name", "Researcher")
    pdf_path = generate_single_paper_pdf(paper, user_name=user_name)
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    st.download_button(
        label="📥 Download Report (PDF)",
        data=pdf_bytes,
        file_name=f"MindSeek_Report_{paper['id']}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

# GitHub Repositories Section
if show_repos:
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.markdown(f"### GitHub Code for *{method_val}*")
    
    repos = paper.get("github_repos") or []
    if repos:
        r_cols = st.columns(len(repos[:3]))
        for idx, repo in enumerate(repos[:3]):
            with r_cols[idx]:
                stars_display = f"{repo.get('stars', 0):,}"
                r_name = repo.get('name', 'Repository')
                r_desc = repo.get('description', '')
                r_lang = repo.get('language', 'Python')
                r_url = repo.get('url', '#')

                repo_card_html = f"""<div class="repo-card">
<div style="display: flex; justify-content: space-between; align-items: flex-start;">
<strong style="color: #1A1A1A; font-size: 0.95rem;">{r_name}</strong>
<span style="font-size: 0.8rem; background: #FFF8E7; border: 1px solid #FFE4A0; padding: 2px 8px; border-radius: 12px; color: #B27B00; font-weight: 600;">
⭐ {stars_display}
</span>
</div>
<p style="font-size: 0.82rem; color: #666666; margin: 10px 0; height: 44px; overflow: hidden; text-overflow: ellipsis;">
{r_desc}
</p>
<div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.78rem;">
<span style="color: #888888;">{r_lang}</span>
<a href="{r_url}" target="_blank" style="color: #0E8A8A; font-weight: 600; text-decoration: none;">View Code ➔</a>
</div>
</div>"""
                st.markdown(repo_card_html, unsafe_allow_html=True)
    else:
        st.info("No GitHub repositories found for this methodology.")
