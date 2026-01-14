import os
from pypdf import PdfReader

def extract_text_from_pdf(filepath: str) -> dict:
    try:
        reader = PdfReader(filepath)
        text = "\n".join([page.extract_text() or "" for page in reader.pages])
        return {"full_text": text, "meta": reader.metadata or {}}
    except Exception as e:
        print(f"[ERROR] PDF Read Failed: {e}")
        return None
