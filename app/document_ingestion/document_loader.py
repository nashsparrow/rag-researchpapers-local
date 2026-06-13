import os
import pymupdf


def validate(pdf_path):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    if not pdf_path.lower().endswith(".pdf"):
        raise ValueError(f"Invalid file type: {pdf_path}. Expected a PDF file.")

    # validate not empty
    if os.path.getsize(pdf_path) == 0:
        raise ValueError(f"PDF file is empty: {pdf_path}")

    # validate readable
    try:
        with open(pdf_path, "rb") as f:
            f.read(1)
    except Exception as e:
        raise ValueError(f"PDF file is not readable: {pdf_path}. Error: {str(e)}")

    # validate not too large (e.g., 100MB)
    if os.path.getsize(pdf_path) > 100 * 1024 * 1024:
        raise ValueError(
            f"PDF file is too large: {pdf_path}. Maximum allowed size is 100MB."
        )


def load_pdf_to_document(pdf_path):
    validate(pdf_path)
    doc = pymupdf.open(pdf_path)
    return doc
