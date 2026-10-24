import re

WHITELIST_METHODOLOGIES = [
    "CLIP", "ViT", "CNN", "YOLO", "Transformer", "ResNet", "BERT", "LLM", "Diffusion", "GAN", "U-Net"
]

# Aliases and variants mapped to whitelist canonical names
METHODOLOGY_ALIASES = {
    "yolov11": "YOLO", "yolov10": "YOLO", "yolov9": "YOLO", "yolov8": "YOLO", "yolov7": "YOLO", "yolov5": "YOLO", "yolov4": "YOLO", "yolov3": "YOLO", "yolo": "YOLO",
    "resnet-152": "ResNet", "resnet-101": "ResNet", "resnet-50": "ResNet", "resnet-34": "ResNet", "resnet-18": "ResNet", "resnet": "ResNet", "resnext": "ResNet",
    "vision transformer": "ViT", "swin transformer": "Transformer", "transformer": "Transformer", "vit": "ViT", "deit": "ViT",
    "bert": "BERT", "roberta": "BERT", "scibert": "BERT", "biobert": "BERT", "distilbert": "BERT", "deberta": "BERT",
    "llm": "LLM", "llama": "LLM", "gpt-4": "LLM", "gpt-3": "LLM", "gpt": "LLM", "mistral": "LLM",
    "cnn": "CNN", "convolutional neural network": "CNN", "densenet": "CNN", "mobilenet": "CNN", "efficientnet": "CNN",
    "stable diffusion": "Diffusion", "diffusion model": "Diffusion", "diffusion": "Diffusion", "ddpm": "Diffusion",
    "gan": "GAN", "cyclegan": "GAN", "dcgan": "GAN", "pix2pix": "GAN",
    "u-net": "U-Net", "unet": "U-Net",
    "openai clip": "CLIP", "contrastive language-image pre-training": "CLIP"
}

VERBS_TO_NEVER_USE = {
    "investigated", "signing", "proposed", "proposing", "utilizing", "using", "learning",
    "training", "evaluating", "designing", "comparing", "optimizing", "benchmarking",
    "analyzing", "studying", "measuring", "processing", "method", "approach", "framework",
    "architecture", "model", "paper", "author", "baseline", "system", "performance"
}

KNOWN_DATASETS = [
    "MS COCO", "COCO", "ImageNet-1k", "ImageNet-22k", "ImageNet", "CIFAR-100", "CIFAR-10", "CIFAR",
    "MNIST", "Fashion-MNIST", "EMNIST", "SVHN",
    "Pascal VOC", "VOC2007", "VOC2012", "Cityscapes", "KITTI", "Waymo Open Dataset", "Waymo", "BDD100K",
    "SQuAD 2.0", "SQuAD", "GLUE", "SuperGLUE", "IMDb", "AG News",
    "MIMIC-III", "MIMIC-IV", "CheXpert", "NIH Chest X-ray", "COVID-19 Radiography",
    "CelebA", "LFW", "Wider Face", "Open Images", "ADE20K"
]

def clean_dataset_name(raw_name: str, full_text: str) -> str:
    """Fixes truncation issues like '-specific' by finding full context."""
    if not raw_name:
        return "Benchmark Dataset"
    
    clean = raw_name.strip()
    
    # If dataset starts with a hyphen or equals '-specific'
    if clean.startswith("-") or clean.lower() in ["-specific", "specific"]:
        match = re.search(r"(\b[A-Za-z0-9]+\-specific\b)", full_text, flags=re.IGNORECASE)
        if match:
            clean = match.group(1)
        else:
            clean = "Domain-Specific Dataset"
            
    # Clean leading/trailing punctuation
    clean = re.sub(r"^[\-\_\,\:\s]+|[\-\_\,\:\s]+$", "", clean)
    return clean if clean else "Benchmark Dataset"

def extract_entities(text: str, full_document_text: str = "") -> dict:
    """
    Extracts methodology using STRICT WHITELIST only.
    If not in whitelist or recognized variants, returns 'Not specified'.
    NEVER returns verbs like 'investigated', 'signing', or 'proposed'.
    """
    corpus = (text or "") + "\n" + (full_document_text or "")
    corpus_lower = corpus.lower()

    # 1. Methodology Extraction - Check Whitelist & Aliases
    detected_methodology = None

    # Check for CLIP specifically (must be uppercase CLIP or OpenAI CLIP, NOT English verb 'clip')
    if re.search(r"\bCLIP\b", corpus) or re.search(r"\b(?:openai[\s\-]clip|contrastive\s+language[\-\s]image)\b", corpus, flags=re.IGNORECASE):
        detected_methodology = "CLIP"

    # Check for direct whitelist aliases
    if not detected_methodology:
        for alias, canonical in METHODOLOGY_ALIASES.items():
            if alias.lower() == "clip":
                continue
            pattern = r"\b" + re.escape(alias) + r"\b"
            if re.search(pattern, corpus, flags=re.IGNORECASE):
                detected_methodology = canonical
                # If explicit version like YOLOv8 or ResNet-50 was found, prefer the specific term
                spec_match = re.search(r"\b(YOLOv\d+|ResNet\-\d+|ViT\-[A-Za-z0-9]+)\b", corpus, flags=re.IGNORECASE)
                if spec_match:
                    detected_methodology = spec_match.group(1)
                break

    if not detected_methodology:
        for w in WHITELIST_METHODOLOGIES:
            if w == "CLIP":
                continue
            pattern = r"\b" + re.escape(w) + r"\b"
            if re.search(pattern, corpus, flags=re.IGNORECASE):
                detected_methodology = w
                break

    # Strictly reject any blacklist verbs
    if detected_methodology and detected_methodology.lower() in VERBS_TO_NEVER_USE:
        detected_methodology = None

    if not detected_methodology:
        detected_methodology = "Not specified"

    # 2. Dataset Extraction
    detected_dataset = None
    for kd in KNOWN_DATASETS:
        pattern = r"\b" + re.escape(kd) + r"\b"
        if re.search(pattern, corpus, flags=re.IGNORECASE):
            detected_dataset = kd
            break

    DATASET_STOPWORDS = {
        "specific", "each", "any", "this", "that", "every", "our", "the", "their",
        "new", "all", "various", "multiple", "several", "different", "given", "same",
        "whole", "full", "single", "both", "one", "two", "three", "first", "second",
        "custom", "private", "public", "large", "small", "real", "synthetic", "raw"
    }

    if not detected_dataset:
        # Pattern like "on the [Name] dataset"
        d_matches = re.finditer(r"(?:on|using|evaluated on|benchmarked on)\s+(?:the\s+)?([A-Za-z0-9\-\_]+)\s+(?:dataset|benchmark|corpus)", corpus, flags=re.IGNORECASE)
        for d_match in d_matches:
            candidate = d_match.group(1).strip()
            if candidate.lower() not in VERBS_TO_NEVER_USE and candidate.lower() not in DATASET_STOPWORDS and len(candidate) > 2:
                detected_dataset = candidate
                break

    # Apply dataset truncation fix (e.g. handle '-specific')
    final_dataset = clean_dataset_name(detected_dataset, corpus)

    return {
        "methodology": detected_methodology,
        "dataset": final_dataset
    }
