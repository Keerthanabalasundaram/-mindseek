import os
import sys

from utils.docling_extractor import extract_text_from_pdf
from utils.section_cutter import cut_methodology_section
from utils.scispacy_extractor import extract_entities
from utils.accuracy_extractor import extract_accuracy
from utils.github_api import search_github_repos
from utils.db import init_db, get_or_create_user, save_paper, get_paper, save_comparison, get_papers_by_ids
from utils.report_generator import generate_comparison_pdf, generate_single_paper_pdf

def test_full_flow():
    print("--- 1. Testing PDF text extraction ---")
    pdf_path = "samples/IEEE_Paper1_YOLOv8_COCO.pdf"
    text, engine = extract_text_from_pdf(pdf_path)
    print(f"Extractor Engine used: {engine}")
    print(f"Extracted characters: {len(text)}")
    assert len(text) > 100, "Extracted text is too short!"

    print("\n--- 2. Testing Section Cutter ---")
    method_text, status = cut_methodology_section(text)
    print(f"Section cutter status: {status}")
    print(f"Methodology text length: {len(method_text)}")
    assert len(method_text) > 50, "Methodology section empty!"

    print("\n--- 3. Testing SciSpacy NLP entity extraction ---")
    ent = extract_entities(method_text, text)
    print(f"Extracted Methodology: '{ent['methodology']}'")
    print(f"Extracted Dataset: '{ent['dataset']}'")
    assert "YOLO" in ent['methodology'], f"Expected YOLO in methodology, got {ent['methodology']}"
    assert "COCO" in ent['dataset'], f"Expected COCO in dataset, got {ent['dataset']}"

    print("\n--- 4. Testing Regex Accuracy Extraction ---")
    acc, metric, cands = extract_accuracy(method_text, text)
    print(f"Extracted Metric: {acc}% ({metric})")
    assert acc == 94.8, f"Expected 94.8%, got {acc}"

    print("\n--- 5. Testing GitHub Search API ---")
    repos = search_github_repos(ent['methodology'])
    print(f"Found {len(repos)} GitHub repositories:")
    for r in repos:
        print(f" - {r['name']} ({r['stars']} stars): {r['url']}")
    assert len(repos) >= 1, "Expected at least 1 repository"

    print("\n--- 6. Testing Database operations ---")
    init_db()
    user = get_or_create_user("Dr. Alan Turing", "alan@mindseek.ai")
    print(f"User created / fetched: #{user['id']} {user['name']} ({user['email']})")
    
    p1_id = save_paper(user['id'], "IEEE_Paper1_YOLOv8_COCO.pdf", ent['methodology'], ent['dataset'], acc, method_text, repos)
    paper1 = get_paper(p1_id)
    print(f"Saved Paper 1: #{paper1['id']} {paper1['filename']}")

    # Process Paper 2
    p2_path = "samples/IEEE_Paper2_ResNet50_ImageNet.pdf"
    p2_text, _ = extract_text_from_pdf(p2_path)
    p2_m_text, _ = cut_methodology_section(p2_text)
    p2_ent = extract_entities(p2_m_text, p2_text)
    p2_acc, _, _ = extract_accuracy(p2_m_text, p2_text)
    p2_repos = search_github_repos(p2_ent['methodology'])
    p2_id = save_paper(user['id'], "IEEE_Paper2_ResNet50_ImageNet.pdf", p2_ent['methodology'], p2_ent['dataset'], p2_acc, p2_m_text, p2_repos)
    print(f"Saved Paper 2: #{p2_id} {p2_ent['methodology']} | {p2_ent['dataset']} | {p2_acc}%")

    print("\n--- 7. Testing PDF Report Generation ---")
    single_pdf = generate_single_paper_pdf(paper1, user_name=user['name'])
    print(f"Generated Single Paper PDF: {single_pdf} (size: {os.path.getsize(single_pdf)} bytes)")
    assert os.path.exists(single_pdf) and os.path.getsize(single_pdf) > 1000

    papers = get_papers_by_ids([p1_id, p2_id])
    rec = {
        "blueprint": "To make it 10/10, combine YOLOv8 with ImageNet and add BiFPN multi-scale feature pyramids.",
        "best_methodology": "YOLOv8",
        "best_dataset": "ImageNet"
    }
    comp_pdf = generate_comparison_pdf(papers, rec, user_name=user['name'])
    print(f"Generated Comparison PDF: {comp_pdf} (size: {os.path.getsize(comp_pdf)} bytes)")
    assert os.path.exists(comp_pdf) and os.path.getsize(comp_pdf) > 1000

    comp_id = save_comparison(user['id'], [p1_id, p2_id], comp_pdf)
    print(f"Saved Comparison session #{comp_id} to database.")

    print("\n==========================================")
    print(">>> ALL PIPELINE TESTS PASSED 100%! <<<")
    print("==========================================")

if __name__ == "__main__":
    test_full_flow()
