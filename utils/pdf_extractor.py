import pymupdf


def extract_text_from_pdf(pdf_path):
    """
    Extract text from all pages of a PDF resume.
    """

    text = ""

    try:
        document = pymupdf.open(pdf_path)

        for page in document:
            text += page.get_text()

        document.close()

    except Exception as e:
        raise RuntimeError(f"Could not read PDF: {e}")

    return text.strip()