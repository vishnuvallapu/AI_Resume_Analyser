import fitz


def extract_resume_text(pdf_bytes):
    try:
        document = fitz.open(
            stream=pdf_bytes,
            filetype="pdf"
        )

        try:
            if document.page_count == 0:
                raise ValueError("The PDF has no pages")

            if document.page_count > 20:
                raise ValueError("PDF must contain 20 pages or fewer")

            text = "\n".join(
                page.get_text() for page in document
            ).strip()

            if len(text) < 30:
                raise ValueError(
                    "No readable text found. "
                    "This may be a scanned PDF."
                )

            return text

        finally:
            document.close()

    except fitz.FileDataError as error:
        raise ValueError("The uploaded PDF is invalid") from error