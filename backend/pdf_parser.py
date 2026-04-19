import fitz

def extract_text_from_pdf(pdf_path: str) -> str:
    all_text = ""
    document = fitz.open(pdf_path)
    for page in document:
        text = page.get_text()
        all_text = all_text + text
    return all_text