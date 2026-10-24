import requests
import urllib.parse

# Curated fallback repos for common ML/DL architectures if GitHub API is offline or rate-limited
CURATED_FALLBACK_REPOS = {
    "yolo": [
        {"name": "ultralytics/ultralytics", "stars": 34500, "url": "https://github.com/ultralytics/ultralytics", "description": "NEW - YOLOv8, YOLOv9, and YOLOv11 in PyTorch > ONNX > OpenVINO > CoreML > TFLite", "language": "Python"},
        {"name": "WongKinYiu/yolov7", "stars": 14200, "url": "https://github.com/WongKinYiu/yolov7", "description": "Implementation of paper - YOLOv7: Trainable bag-of-freebies sets new state-of-the-art for real-time object detectors", "language": "Python"},
        {"name": "ultralytics/yolov5", "stars": 52100, "url": "https://github.com/ultralytics/yolov5", "description": "YOLOv5 in PyTorch > ONNX > CoreML > TFLite", "language": "Python"}
    ],
    "resnet": [
        {"name": "pytorch/vision", "stars": 16400, "url": "https://github.com/pytorch/vision", "description": "Datasets, Transforms and Models specific to Computer Vision including Deep ResNet backbones", "language": "Python"},
        {"name": "KaimingHe/deep-residual-networks", "stars": 5400, "url": "https://github.com/KaimingHe/deep-residual-networks", "description": "Deep Residual Learning for Image Recognition - official Caffe/Torch code", "language": "Python"},
        {"name": "facebookresearch/ResNeXt", "stars": 2300, "url": "https://github.com/facebookresearch/ResNeXt", "description": "Aggregated Residual Transformations for Deep Neural Networks", "language": "Lua/Python"}
    ],
    "bert": [
        {"name": "google-research/bert", "stars": 38100, "url": "https://github.com/google-research/bert", "description": "TensorFlow code and pre-trained models for BERT", "language": "Python"},
        {"name": "huggingface/transformers", "stars": 134000, "url": "https://github.com/huggingface/transformers", "description": "Transformers: State-of-the-art Machine Learning for Pytorch, TensorFlow, and JAX", "language": "Python"},
        {"name": "allenai/scibert", "stars": 1700, "url": "https://github.com/allenai/scibert", "description": "A pretrained language model for scientific text", "language": "Python"}
    ],
    "transformer": [
        {"name": "huggingface/transformers", "stars": 134000, "url": "https://github.com/huggingface/transformers", "description": "State-of-the-art Machine Learning for PyTorch, TensorFlow, and JAX", "language": "Python"},
        {"name": "lucidrains/vit-pytorch", "stars": 15800, "url": "https://github.com/lucidrains/vit-pytorch", "description": "Implementation of Vision Transformer in PyTorch", "language": "Python"},
        {"name": "microsoft/Swin-Transformer", "stars": 12800, "url": "https://github.com/microsoft/Swin-Transformer", "description": "Hierarchical Vision Transformer using Shifted Windows", "language": "Python"}
    ],
    "cnn": [
        {"name": "keras-team/keras", "stars": 62000, "url": "https://github.com/keras-team/keras", "description": "Deep Learning for humans - High-level neural networks API", "language": "Python"},
        {"name": "Cadene/pretrained-models.pytorch", "stars": 8200, "url": "https://github.com/Cadene/pretrained-models.pytorch", "description": "Pretrained ConvNets for PyTorch: ResNet, ResNeXt, DenseNet, Inception", "language": "Python"},
        {"name": "rwightman/pytorch-image-models", "stars": 31000, "url": "https://github.com/huggingface/pytorch-image-models", "description": "PyTorch image models, scripts, pretrained weights (timm)", "language": "Python"}
    ],
    "default": [
        {"name": "paperswithcode/paperswithcode-data", "stars": 5900, "url": "https://github.com/paperswithcode/paperswithcode-data", "description": "The mission of Papers With Code is to create a free and open resource with Machine Learning papers, code and evaluation tables.", "language": "Python"},
        {"name": "huggingface/transformers", "stars": 134000, "url": "https://github.com/huggingface/transformers", "description": "State-of-the-art Machine Learning for PyTorch, TensorFlow, and JAX", "language": "Python"},
        {"name": "pytorch/pytorch", "stars": 85000, "url": "https://github.com/pytorch/pytorch", "description": "Tensors and Dynamic neural networks in Python with strong GPU acceleration", "language": "C++/Python"}
    ]
}

def search_github_repos(methodology: str) -> list[dict]:
    """
    Searches GitHub for top 3 repositories associated with the extracted methodology.
    Endpoint: https://api.github.com/search/repositories?q={methodology}+stars:>100
    Includes fallback cache for rate-limited requests or offline operation.
    """
    clean_query = methodology.strip()
    # Remove slash variants or extra tokens for better search query
    search_term = clean_query.split("/")[0].strip()
    if not search_term or search_term.lower() in ["n/a", "none", "unknown"]:
        search_term = "machine learning"

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "MindSeek-Research-Comparator/1.0"
    }

    url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(search_term)}+stars:>100&sort=stars&order=desc&per_page=3"

    try:
        response = requests.get(url, headers=headers, timeout=6)
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            repos = []
            for item in items[:3]:
                repos.append({
                    "name": item.get("full_name", item.get("name")),
                    "stars": item.get("stargazers_count", 0),
                    "url": item.get("html_url", ""),
                    "description": (item.get("description") or "No description provided.")[:140],
                    "language": item.get("language") or "Python"
                })
            if repos:
                return repos
    except Exception as e:
        print(f"[GitHub API] API request error: {e}. Using curated repository fallback.")

    # Fallback to curated repositories based on keyword
    term_lower = search_term.lower()
    for key, repo_list in CURATED_FALLBACK_REPOS.items():
        if key in term_lower:
            return repo_list

    return CURATED_FALLBACK_REPOS["default"]
