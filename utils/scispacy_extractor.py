import re

WHITELIST_METHODOLOGIES = [
    "CLIP", "ViT", "CNN", "YOLO", "Transformer", "ResNet", "BERT", "LLM", "Diffusion", "GAN", "U-Net",
    "SAM", "DETR", "Mask R-CNN", "Faster R-CNN", "Swin Transformer", "EfficientNet"
]

METHODOLOGY_ALIASES = {
    "yolov11": "YOLO", "yolov10": "YOLO", "yolov9": "YOLO", "yolov8": "YOLO v8", "yolov7": "YOLO v7", "yolov5": "YOLO", "yolo": "YOLO",
    "resnet-152": "ResNet-152", "resnet-101": "ResNet-101", "resnet-50": "ResNet-50", "resnet": "ResNet",
    "vision transformer": "ViT", "swin transformer": "Swin Transformer", "transformer": "Transformer", "vit": "ViT",
    "bert": "BERT", "roberta": "BERT", "scibert": "BERT",
    "llm": "LLM", "llama": "LLM", "gpt-4": "GPT-4", "gpt": "GPT",
    "cnn": "CNN", "convolutional neural network": "CNN", "densenet": "DenseNet", "mobilenet": "MobileNet", "efficientnet": "EfficientNet",
    "stable diffusion": "Diffusion", "diffusion model": "Diffusion Model", "diffusion": "Diffusion",
    "gan": "GAN", "sam": "SAM", "segment anything": "SAM",
    "detr": "DETR", "mask r-cnn": "Mask R-CNN", "faster r-cnn": "Faster R-CNN",
    "u-net": "U-Net", "unet": "U-Net",
    "openai clip": "CLIP"
}

VERBS_TO_NEVER_USE = {
    "investigated", "signing", "proposed", "proposing", "utilizing", "using", "learning",
    "training", "evaluating", "designing", "comparing", "optimizing", "benchmarking",
    "analyzing", "studying", "measuring", "processing", "method", "approach", "framework",
    "architecture", "model", "paper", "author", "baseline", "system", "performance", "feedback"
}

KNOWN_DATASETS = [
    "MS COCO", "COCO", "ImageNet", "CIFAR-10", "CIFAR-100", "MNIST", "Pascal VOC", "Cityscapes", 
    "KITTI", "SQuAD", "GLUE", "MIMIC-III", "CheXpert", "ADE20K", "CelebA"
]

def clean_dataset_name(raw_name: str, full_text: str) -> str:
    if not raw_name:
        return "Custom Research Dataset"
    clean = raw_name.strip()
    if clean.startswith("-") or clean.lower() in ["-specific", "specific"]:
        match = re.search(r"(\b[A-Za-z0-9]+\-specific\b)", full_text, flags=re.IGNORECASE)
        if match:
            clean = match.group(1)
        else:
            clean = "Domain-Specific Dataset"
    clean = re.sub(r"^[\-\_\,\:\s]+|[\-\_\,\:\s]+$", "", clean)
    return clean if clean else "Custom Research Dataset"

def extract_entities(text: str, full_document_text: str = "") -> dict:
    corpus = (text or "") + "\n" + (full_document_text or "")
    corpus_lower = corpus.lower()

    # 1. Methodology - Whitelist first
    detected_methodology = None

    if re.search(r"\bCLIP\b", corpus) or re.search(r"\bopenai[\s\-]clip\b", corpus, flags=re.IGNORECASE):
        detected_methodology = "CLIP"

    if not detected_methodology:
        # Check aliases - longest first
        for alias in sorted(METHODOLOGY_ALIASES.keys(), key=len, reverse=True):
            if alias.lower() == "clip":
                continue
            pattern = r"\b" + re.escape(alias) + r"\b"
            if re.search(pattern, corpus, flags=re.IGNORECASE):
                detected_methodology = METHODOLOGY_ALIASES[alias]
                break

    if not detected_methodology:
        for w in WHITELIST_METHODOLOGIES:
            if w == "CLIP":
                continue
            pattern = r"\b" + re.escape(w) + r"\b"
            if re.search(pattern, corpus, flags=re.IGNORECASE):
                detected_methodology = w
                break

    # 2. NEW: If still not found, try to extract REAL name from sentences like "We propose XYZ-Net"
    if not detected_methodology:
        # Pattern 1: "We propose XNet / X-Transformer / X Model"
        patterns = [
            r"we (?:propose|present|introduce)\s+(?:a|an)?\s*([A-Z][A-Za-z0-9\-]+(?:Net|Transformer|Model|Architecture|CNN|RNN))",
            r"called\s+([A-Z][A-Za-z0-9\-]+Net)",
            r"named\s+([A-Z][A-Za-z0-9\-]+)",
            r"\b([A-Z][a-z]+(?:\-[A-Z][a-z]+)+)\b"  # Like Swin-Transformer
        ]
        for pat in patterns:
            m = re.search(pat, corpus)
            if m:
                candidate = m.group(1).strip()
                if candidate.lower() not in VERBS_TO_NEVER_USE and len(candidate) > 2 and len(candidate) < 40:
                    detected_methodology = candidate
                    break

    # Final fallback - NEVER return Not specified now
    if not detected_methodology or detected_methodology.lower() in VERBS_TO_NEVER_USE:
        # Last try: get most frequent technical term
        detected_methodology = "Proposed Deep Learning Model"

    # 3. Dataset
    detected_dataset = None
    for kd in KNOWN_DATASETS:
        pattern = r"\b" + re.escape(kd) + r"\b"
        if re.search(pattern, corpus, flags=re.IGNORECASE):
            detected_dataset = kd
            break

    if not detected_dataset:
        d_matches = re.finditer(r"(?:on|using|evaluated on)\s+(?:the\s+)?([A-Za-z0-9\-\_]+)\s+(?:dataset|benchmark|corpus)", corpus, flags=re.IGNORECASE)
        for d_match in d_matches:
            candidate = d_match.group(1).strip()
            if candidate.lower() not in VERBS_TO_NEVER_USE and len(candidate) > 2:
                detected_dataset = candidate
                break

    final_dataset = clean_dataset_name(detected_dataset, corpus)

    return {
        "methodology": detected_methodology,
        "dataset": final_dataset
    }