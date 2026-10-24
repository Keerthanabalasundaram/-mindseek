import os
from fpdf import FPDF

def create_sample_ieee_paper(filename, title, authors, abstract, methodology, dataset, accuracy_str, results_text):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # IEEE Header
    pdf.set_font("Times", "I", 9)
    pdf.cell(0, 5, "IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE", ln=True, align="C")
    pdf.ln(4)

    # Title
    pdf.set_font("Times", "B", 18)
    pdf.multi_cell(0, 8, title, align="C")
    pdf.ln(2)

    # Authors
    pdf.set_font("Times", "", 10)
    pdf.cell(0, 5, authors, ln=True, align="C")
    pdf.ln(5)

    # Abstract & Keywords (single column block)
    pdf.set_font("Times", "B", 9)
    pdf.cell(20, 5, "Abstract-")
    pdf.set_font("Times", "I", 9)
    pdf.multi_cell(0, 5, abstract)
    pdf.ln(4)

    # Section I. INTRODUCTION
    pdf.set_font("Times", "B", 11)
    pdf.cell(0, 6, "I. INTRODUCTION", ln=True)
    pdf.set_font("Times", "", 10)
    intro = (
        "Modern computer vision models have experienced dramatic evolution. Developing architectures that "
        "balance latency and feature selectivity remains a central topic of inquiry in machine intelligence."
    )
    pdf.multi_cell(0, 5, intro)
    pdf.ln(4)

    # Section II. RELATED WORK
    pdf.set_font("Times", "B", 11)
    pdf.cell(0, 6, "II. RELATED WORK", ln=True)
    pdf.set_font("Times", "", 10)
    pdf.multi_cell(0, 5, "Prior approaches often struggled with dense multi-scale object distributions.")
    pdf.ln(4)

    # Section III. PROPOSED METHODOLOGY
    pdf.set_font("Times", "B", 11)
    pdf.cell(0, 6, "III. PROPOSED METHODOLOGY", ln=True)
    pdf.set_font("Times", "", 10)
    method_body = (
        f"In this section, we delineate our proposed framework. The core system architecture employs {methodology}. "
        f"We integrate asymptotic multi-level feature pyramid routing, connecting cross-layer feature maps "
        f"with learned convolutional kernels. Training is executed over the {dataset} benchmark. "
        "The loss formulation balances bounding-box focal regression with cross-entropy classification."
    )
    pdf.multi_cell(0, 5, method_body)
    pdf.ln(4)

    # Section IV. EXPERIMENTAL RESULTS
    pdf.set_font("Times", "B", 11)
    pdf.cell(0, 6, "IV. EXPERIMENTAL RESULTS", ln=True)
    pdf.set_font("Times", "", 10)
    exp_body = (
        f"To evaluate the proposed model, extensive experiments were conducted on {dataset}. "
        f"The proposed architecture achieved {accuracy_str}. "
        f"{results_text}"
    )
    pdf.multi_cell(0, 5, exp_body)
    pdf.ln(4)

    # Section V. CONCLUSION
    pdf.set_font("Times", "B", 11)
    pdf.cell(0, 6, "V. CONCLUSION", ln=True)
    pdf.set_font("Times", "", 10)
    pdf.multi_cell(0, 5, "In this work, we introduced a novel framework that improves upon established baselines.")
    
    pdf.output(filename)
    print(f"Generated sample IEEE PDF: {filename}")

if __name__ == "__main__":
    samples_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    
    # Paper 1
    create_sample_ieee_paper(
        os.path.join(samples_dir, "IEEE_Paper1_YOLOv8_COCO.pdf"),
        "YOLOv8-AFPN: Asymptotic Feature Pyramid Network for Real-Time Object Detection",
        "Dr. Eleanor Vance, Senior Member, IEEE, and Dr. Marcus Thorne",
        "Object detection in complex urban scenes requires high representational fidelity and minimal latency. We present an improved YOLOv8 model.",
        "YOLOv8 with Asymptotic Feature Pyramids",
        "MS COCO",
        "94.8% mAP accuracy",
        "Comparative evaluations demonstrate substantial improvements over previous YOLO iterations on small objects."
    )

    # Paper 2
    create_sample_ieee_paper(
        os.path.join(samples_dir, "IEEE_Paper2_ResNet50_ImageNet.pdf"),
        "Deep Residual Squeeze Networks for Large-Scale Visual Recognition",
        "Prof. Julian Sterling, Fellow, IEEE",
        "Deep residual learning allows training networks with hundreds of layers. We evaluate channel attention enhancements.",
        "ResNet-50 with Channel Attention Blocks",
        "ImageNet",
        "91.4% top-1 accuracy",
        "Validation top-1 accuracy is benchmarked with low computational FLOP count compared to standard backbones."
    )

    # Paper 3
    create_sample_ieee_paper(
        os.path.join(samples_dir, "IEEE_Paper3_BERT_SQuAD.pdf"),
        "Contextual Attention Transduction for Question Answering and Semantic Extraction",
        "Dr. Sarah Lin and Dr. David Chen, Member, IEEE",
        "Bidirectional encoder representations offer rich sentence embeddings for reading comprehension.",
        "BERT Transformer with Rotary Positional Embeddings",
        "SQuAD 2.0",
        "88.7% F1 accuracy",
        "The model achieves high linguistic understanding across dense textual passages."
    )
