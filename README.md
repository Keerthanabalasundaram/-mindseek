# MindSeek: Intelligent Research Paper Comparator
> *"Seek the Mind of Every Paper"*

MindSeek is an academic intelligence application designed for researchers to decompose, extract, benchmark, and compare peer-reviewed IEEE 2-column research papers.

---

## 🌟 Key Features

1. **Academic Paper Desk Aesthetic**:
   - Styled after an academic researcher's desk with subtle `#FFFEF9` paper texture, notebook-ruled upload dropzones, sticky note diagnostic cards, and custom typography (`Merriweather` + `Inter`).
   - Rotating archival quote banner every 3 seconds.
   - Floating background keyword animations.

2. **IBM Docling 2-Column Extraction (with PyMuPDF fallback)**:
   - Accurately decomposes complex IEEE 2-column layouts without line interweaving.
   - Preserves document geometry, mathematical expressions, and structural headings.

3. **Intelligent Methodology Section Cutter (Regex)**:
   - Isolates the exact Methodology / Proposed Architecture section (from headings like `III. METHODOLOGY`, `Proposed Method`, `Approach` up to `Results`, `Experiments`, or `Conclusion`).

4. **SciSpacy NLP Entity Recognition (`en_core_sci_sm`)**:
   - Discovers domain models (`YOLOv8`, `CNN`, `ResNet`, `BERT`, `Transformer`, `ViT`, `GAN`, etc.) and benchmarks/datasets (`MS COCO`, `ImageNet`, `MNIST`, `CIFAR`, `SQuAD`, etc.).
   - Auto-downloads and mounts `en_core_sci_sm` natively in code.

5. **Regex Metric & Accuracy Profiling**:
   - Extracts reported accuracy, mAP, precision, and F1 scores using contextual regex patterns.

6. **Live GitHub Repository Discovery**:
   - Queries GitHub Search API for the top starred repositories matching the extracted methodology (`q={methodology}+stars:>100`).

7. **Multi-Paper Comparative Synthesis & 10/10 AI Blueprint**:
   - Academic comparison matrix table with deduced best features.
   - Dual visual distribution: Plotly accuracy comparison bar chart and methodology distribution donut chart.
   - Paper-by-paper critical pros/cons review.
   - Expert AI synthesis: Suggests concrete architectural augmentations (e.g., BiFPN, small object detection heads, attention mechanisms) and dataset scaling to turn the research into a 10/10 SOTA paper.

8. **PDF Report Generation (`fpdf2`)**:
   - One-click export of comparison reports and individual paper diagnostic briefs with embedded charts and reviews.

9. **Persistent Research Ledger (SQLite)**:
   - Stores user profiles, analyzed papers, and past comparison sessions in `mindseek.db`.

---

## 🚀 Quickstart Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📂 Project Architecture

```
/MindSeek
  app.py                        # Landing page, A4 card login, quotes carousel & routing
  requirements.txt              # Complete dependency specification
  mindseek.db                   # SQLite database (auto-created on first run)
  /pages
    1_Home_Upload.py            # Single IEEE paper upload dropzone & researcher metrics
    2_Single_Result.py          # Open research paper desk layout, sticky notes & Plotly chart
    3_Compare.py                # Multi-paper upload (up to 10) & stacked paper preview
    4_Comparison_Dashboard.py   # Matrix table, dual charts, 10/10 synthesis, & PDF export
    5_History.py                # Past paper extractions & re-downloadable comparative reports
  /utils
    docling_extractor.py        # IBM Docling parser with 2-column PyMuPDF fallback
    section_cutter.py           # Regex-based methodology section isolation
    scispacy_extractor.py       # SciSpacy + en_core_sci_sm model loader & entity extraction
    accuracy_extractor.py       # Metric & accuracy percentage regex parser
    github_api.py               # GitHub repository search with curated fallbacks
    db.py                       # SQLite database manager (users, papers, comparisons)
    report_generator.py         # fpdf2 comparison & single paper PDF report builder
    ui_helpers.py               # CSS injection and session management helpers
  /assets
    style.css                   # Custom academic desk CSS stylesheet
  /samples
    IEEE_Paper1_YOLOv8_COCO.pdf # Sample IEEE 2-column paper (YOLOv8, MS COCO, 94.8% mAP)
    IEEE_Paper2_ResNet50_ImageNet.pdf # Sample IEEE 2-column paper (ResNet-50, ImageNet, 91.4%)
    IEEE_Paper3_BERT_SQuAD.pdf  # Sample IEEE 2-column paper (BERT, SQuAD 2.0, 88.7% F1)
    create_sample_papers.py     # Generator script for sample IEEE PDFs
```

---

## 🧪 Testing

To run the automated end-to-end integration test:
```bash
python test_pipeline.py
```
