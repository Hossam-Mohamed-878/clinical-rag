import json
import os
import re
from pathlib import Path

import fitz  # PyMuPDF

# Directory containing this script — treat as project root
src_dir = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(src_dir)
source_dir = os.path.join(PROJECT_ROOT, "data","source")       # if PDFs are in a subfolder
output_dir = os.path.join(PROJECT_ROOT, "data", "extracted")

def clean_text(text: str) -> str:
    text = re.sub(r'-\n(?=[a-z])', '', text)
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    text = text.replace('\ufb01', 'fi').replace('\ufb02', 'fl')
    return text.strip()

def extract_pdf(pdf_path: str) -> dict:
    doc = fitz.open(pdf_path)
    total_pages = doc.page_count  # capture before closing
    pages = []

    for i, page in enumerate(doc):
        raw = page.get_text("text")
        cleaned = clean_text(raw)
        if cleaned:
            pages.append({
                "page_number": i + 1,
                "text": cleaned,
                "char_count": len(cleaned)
            })

    doc.close()  # safe to close now, nothing after this touches doc

    return {
        "source": Path(pdf_path).name,
        "total_pages": total_pages,
        "extracted_pages": len(pages),
        "pages": pages
    }

def process_directory(root_dir: str = ".", out_dir: str = "output/extracted") -> dict:
    pdf_files = [f for f in os.listdir(root_dir) if f.lower().endswith(".pdf")]

    corpus = {"documents": []}

    for pdf_file in pdf_files:
        pdf_path = os.path.join(root_dir, pdf_file)
        doc_data = extract_pdf(pdf_path)
        corpus["documents"].append(doc_data)

        out_path = os.path.join(out_dir, f"{Path(pdf_file).stem}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(doc_data, f, ensure_ascii=False, indent=2)

        print(f"Extracted {doc_data['extracted_pages']} pages from {pdf_file}")

    combined_path = os.path.join(out_dir, "all_documents.json")
    with open(combined_path, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)

    return corpus

if __name__ == "__main__":
    corpus = process_directory(root_dir=source_dir, out_dir=output_dir)
    total_pages = sum(d["extracted_pages"] for d in corpus["documents"])
    print(f"Total documents: {len(corpus['documents'])}, total pages extracted: {total_pages}")