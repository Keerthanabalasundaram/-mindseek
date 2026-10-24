import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path: str) -> tuple[str, str]:
    """
    High-speed text extractor using PyMuPDF (fitz) with column-aware block sorting.
    Executes in < 1 second per paper.
    """
    try:
        doc = fitz.open(pdf_path)
        full_text_pages = []

        for page in doc:
            rect = page.rect
            mid_x = rect.width / 2.0
            blocks = page.get_text("blocks")

            top_blocks = []
            left_blocks = []
            right_blocks = []

            for b in blocks:
                if b[6] == 0:  # Text block
                    x0, y0, x1, y1, text, _, _ = b
                    cleaned_t = text.strip()
                    if not cleaned_t:
                        continue

                    # If block spans across middle or is at top, treat as full-width
                    if (x1 - x0) > (rect.width * 0.65):
                        top_blocks.append((y0, cleaned_t))
                    elif x0 < mid_x and x1 <= (mid_x + 35):
                        left_blocks.append((y0, cleaned_t))
                    else:
                        right_blocks.append((y0, cleaned_t))

            top_blocks.sort(key=lambda item: item[0])
            left_blocks.sort(key=lambda item: item[0])
            right_blocks.sort(key=lambda item: item[0])

            page_content = [t for _, t in (top_blocks + left_blocks + right_blocks)]
            if page_content:
                full_text_pages.append("\n\n".join(page_content))

        doc.close()
        combined_text = "\n\n".join(full_text_pages)
        if len(combined_text.strip()) > 40:
            return combined_text, "PyMuPDF"
    except Exception as e:
        print(f"[PDF Extractor] Error: {e}")

    return "", "None"
