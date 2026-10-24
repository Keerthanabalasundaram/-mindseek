import re

def cut_methodology_section(full_text: str) -> tuple[str, str]:
    """
    Extracts the Methodology section text using Regex.
    Searches for headings such as 'Methodology', 'Proposed Method', 'Approach', 'Architecture'
    up to 'Results', 'Experiments', 'Experimental Evaluation', 'Discussion', 'Conclusion'.

    Returns:
        (extracted_methodology_text, status_message)
    """
    if not full_text or len(full_text.strip()) < 50:
        return "", "Text is too short or empty."

    # Pattern for start headings
    # Matches markdown headers (##), IEEE roman numeral headers (III. METHODOLOGY), or standalone uppercase/title case headers
    start_patterns = [
        r"(?:(?:^|\n)\s*(?:#{1,4}\s*)?(?:[I|V|X\d]+\.?\s*)?(?:III|IV|II|3|4|2)?\.?\s*(?:PROPOSED\s+(?:METHODOLOGY|METHOD|FRAMEWORK|APPROACH|SYSTEM|ARCHITECTURE|MODEL)|METHODOLOGY|METHODS|PROPOSED\s+WORK|SYSTEM\s+ARCHITECTURE|SYSTEM\s+MODEL|MATERIALS\s+AND\s+METHODS|OUR\s+APPROACH)[\s\:\.\-\n])",
        r"(?:(?:^|\n)\s*(?:[I|V|X\d]+\.?\s*)?(?:METHODOLOGY|PROPOSED METHOD|APPROACH)[\s\:\.\-\n])"
    ]

    # Pattern for stop headings
    end_pattern = r"(?:(?:^|\n)\s*(?:#{1,4}\s*)?(?:[I|V|X\d]+\.?\s*)?(?:IV|V|VI|VII|4|5|6|7)?\.?\s*(?:RESULTS\s+AND\s+DISCUSSION|EXPERIMENTAL\s+RESULTS|EXPERIMENTS|EXPERIMENTAL\s+EVALUATION|PERFORMANCE\s+EVALUATION|SIMULATION\s+RESULTS|EVALUATION|RESULTS|DISCUSSION|CONCLUSION|CONCLUSIONS|FUTURE\s+WORK|REFERENCES)[\s\:\.\-\n])"

    # Search with re.IGNORECASE
    for start_pat in start_patterns:
        start_matches = list(re.finditer(start_pat, full_text, flags=re.IGNORECASE))
        if start_matches:
            # Pick the best start match (usually the first clear heading)
            for sm in start_matches:
                start_pos = sm.end()
                sub_text = full_text[start_pos:]
                
                # Search for end heading after start
                end_match = re.search(end_pattern, sub_text, flags=re.IGNORECASE)
                if end_match:
                    end_pos = end_match.start()
                    cut = sub_text[:end_pos].strip()
                    if len(cut) > 150:
                        return cut, "Successfully extracted methodology section."
                else:
                    # If no explicit stop heading found, take up to 4000 characters from start
                    cut = sub_text[:4000].strip()
                    if len(cut) > 150:
                        return cut, "Extracted methodology until document boundary."

    # Fallback: Search for paragraphs mentioning architecture/framework/proposed
    fallback_paragraphs = []
    lines = full_text.split("\n\n")
    for para in lines:
        p_lower = para.lower()
        if any(k in p_lower for k in ["we propose", "proposed method", "our architecture", "pipeline", "framework consists of", "model uses", "backbone", "convolutional", "transformer", "yolo"]):
            fallback_paragraphs.append(para.strip())

    if fallback_paragraphs:
        return "\n\n".join(fallback_paragraphs[:8]), "Extracted methodology via key contextual paragraphs."

    # Safety: Return middle third of document or first 3500 chars if nothing else matched
    mid_start = int(len(full_text) * 0.25)
    mid_end = int(len(full_text) * 0.65)
    return full_text[mid_start:mid_end], "Methodology estimated from core paper body."
