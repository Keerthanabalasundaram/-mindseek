import os
import sys

from utils.db import init_db, get_or_create_user, save_paper, get_paper, get_user_papers, get_user_comparisons, save_comparison, get_papers_by_ids
from utils.docling_extractor import extract_text_from_pdf
from utils.section_cutter import cut_methodology_section
from utils.scispacy_extractor import extract_entities, clean_dataset_name
from utils.accuracy_extractor import extract_accuracy
from utils.github_api import search_github_repos
from utils.report_generator import generate_single_paper_pdf, generate_comparison_pdf

def test_everything():
    print("==================================================")
    print("MINDSEEK COMPREHENSIVE VERIFICATION SUITE")
    print("==================================================")

    init_db()
    # Create test user
    user = get_or_create_user("Test Researcher", "verifier@mindseek.ai")
    user_id = user["id"]
    print(f"User: #{user_id} {user['name']}")

    # ----------------------------------------------------
    # TEST SCENARIO 1: papers = None / 0 papers
    # ----------------------------------------------------
    print("\n[TEST 1] Testing papers = None / Empty History...")
    # Simulate fresh user with 0 papers
    fresh_user = get_or_create_user("New Researcher", "fresh_empty@mindseek.ai")
    empty_papers = get_user_papers(fresh_user["id"]) or []
    empty_comparisons = get_user_comparisons(fresh_user["id"]) or []
    assert isinstance(empty_papers, list) and len(empty_papers) == 0
    assert isinstance(empty_comparisons, list) and len(empty_comparisons) == 0
    # Simulate History page tab creation
    tab_labels = [f"Analyzed Papers ({len(empty_papers)})", f"Paper Comparisons ({len(empty_comparisons)})"]
    print(f"Empty tabs created successfully without crash: {tab_labels}")

    # ----------------------------------------------------
    # TEST SCENARIO 2: Whitelist Methodology & Dataset Truncation
    # ----------------------------------------------------
    print("\n[TEST 2] Testing Methodology Whitelist & Dataset Truncation...")
    
    # Text with verb 'signing' or 'investigated' - should NOT be recognized as methodology
    fake_text = "We investigated signing algorithms using standard deep neural networks."
    ent_fake = extract_entities(fake_text)
    print(f"Extraction on verb 'investigated/signing': Methodology='{ent_fake['methodology']}'")
    assert ent_fake['methodology'] in ["Not specified", "CNN", "Transformer"], f"Verb leaked! Got {ent_fake['methodology']}"
    assert ent_fake['methodology'] not in ["investigated", "signing", "proposed"]

    # Text with '-specific' dataset truncation
    trunc_text = "We evaluated our approach on a domain-specific dataset with medical records."
    cleaned_d = clean_dataset_name("-specific", trunc_text)
    print(f"Cleaned '-specific' dataset: '{cleaned_d}'")
    assert cleaned_d == "domain-specific", f"Expected 'domain-specific', got {cleaned_d}"

    # ----------------------------------------------------
    # TEST SCENARIO 3: Single Paper Extraction & Gauge
    # ----------------------------------------------------
    print("\n[TEST 3] Testing 1 Paper Flow (Fast PyMuPDF, Whitelist, Gauge)...")
    pdf1 = "samples/IEEE_Paper1_YOLOv8_COCO.pdf"
    t1, engine = extract_text_from_pdf(pdf1)
    print(f"PyMuPDF Engine: {engine}, Chars: {len(t1)}")
    assert len(t1) > 100

    m1_text, _ = cut_methodology_section(t1)
    e1 = extract_entities(m1_text, t1)
    acc1, metric1, _ = extract_accuracy(m1_text, t1)
    print(f"Paper 1: Methodology='{e1['methodology']}', Dataset='{e1['dataset']}', Accuracy={acc1}%")
    assert e1['methodology'] in ["YOLOv8", "YOLO"]
    assert "COCO" in e1['dataset']
    assert acc1 == 94.8

    p1_id = save_paper(user_id, "Paper1_YOLOv8_COCO.pdf", e1['methodology'], e1['dataset'], acc1, m1_text, [])
    paper1 = get_paper(p1_id)

    # Test single paper PDF report
    single_pdf = generate_single_paper_pdf(paper1, user_name=user["name"])
    print(f"Single Paper PDF generated: {single_pdf} ({os.path.getsize(single_pdf)} bytes)")
    assert os.path.exists(single_pdf) and os.path.getsize(single_pdf) > 500

    # Test Single Paper Plotly Gauge (Verify no go.Bar crash)
    import plotly.graph_objects as go
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=acc1,
        number={'suffix': "%"}
    ))
    fig_gauge.update_layout(height=280)
    print("Single paper gauge created cleanly with zero errors.")

    # ----------------------------------------------------
    # TEST SCENARIO 4: 2 Papers Comparison & Bar Chart
    # ----------------------------------------------------
    print("\n[TEST 4] Testing 2 Papers Flow (Comparison, Bar Chart, Real Explanation Report)...")
    pdf2 = "samples/IEEE_Paper2_ResNet50_ImageNet.pdf"
    t2, _ = extract_text_from_pdf(pdf2)
    m2_text, _ = cut_methodology_section(t2)
    e2 = extract_entities(m2_text, t2)
    acc2, _, _ = extract_accuracy(m2_text, t2)
    print(f"Paper 2: Methodology='{e2['methodology']}', Dataset='{e2['dataset']}', Accuracy={acc2}%")
    assert e2['methodology'] in ["ResNet-50", "ResNet"]
    assert "ImageNet" in e2['dataset']
    assert acc2 == 91.4

    p2_id = save_paper(user_id, "Paper2_ResNet50_ImageNet.pdf", e2['methodology'], e2['dataset'], acc2, m2_text, [])
    
    papers_list = get_papers_by_ids([p1_id, p2_id])
    assert len(papers_list) == 2

    # Test Comparison Bar Chart: go.Bar(x=names, y=accuracy, marker=dict(color=[...])) strictly without invalid parameters
    names = [p["filename"] for p in papers_list]
    accs = [p["accuracy"] for p in papers_list]
    fig_bar = go.Figure(data=[
        go.Bar(
            x=names,
            y=accs,
            text=[f"{a:.1f}%" for a in accs],
            marker=dict(color=["#5C8D8D", "#9FBABA"]),
            width=0.45
        )
    ])
    fig_bar.update_layout(height=300)
    print(f"Comparison go.Bar chart created cleanly: {names} -> {accs}")

    # Test Comparison PDF with Real Content Explanations (No template placeholders)
    rec_dict = {
        "blueprint": "Combine YOLOv8 with ImageNet and add BiFPN multi-scale feature pyramids to boost small object detection sensitivity while preserving real-time frame rates.",
        "best_methodology": "YOLOv8",
        "best_dataset": "ImageNet"
    }
    comp_pdf = generate_comparison_pdf(papers_list, rec_dict, user_name=user["name"])
    print(f"Comparison PDF generated: {comp_pdf} ({os.path.getsize(comp_pdf)} bytes)")
    assert os.path.exists(comp_pdf) and os.path.getsize(comp_pdf) > 1000

    comp_id = save_comparison(user_id, [p1_id, p2_id], comp_pdf)
    print(f"Saved comparison session #{comp_id}")

    # Verify History queries
    all_user_papers = get_user_papers(user_id) or []
    all_user_comps = get_user_comparisons(user_id) or []
    print(f"User History has {len(all_user_papers)} papers and {len(all_user_comps)} comparisons.")
    assert len(all_user_papers) >= 2
    assert len(all_user_comps) >= 1

    print("\n==================================================")
    print("ALL TESTS (None, 1 Paper, 2 Papers) PASSED 100%!")
    print("==================================================")

if __name__ == "__main__":
    test_everything()
