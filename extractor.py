# extractor.py

# --- Imports ---
import io
import docx
import PyPDF2

# --- File size limits ---
MAX_SIZE_MB = 30
MAX_BYTES = MAX_SIZE_MB * 1024 * 1024

# --- Custom error class ---
class ExtractionError(Exception):
    """Custom exception for extraction-related errors."""
    pass


# --- Check file size before doing anything else ---
def validate_file_size(uploaded_file):
    """
    Ensures the uploaded file does not exceed the maximum allowed size.
    """
    uploaded_file.seek(0, io.SEEK_END)
    size = uploaded_file.tell()
    uploaded_file.seek(0)

    if size > MAX_BYTES:
        raise ExtractionError(f"File exceeds {MAX_SIZE_MB} MB limit.")

    return size


# --- Extract text from a .txt file ---
def extract_text_from_txt(uploaded_file):
    """
    Extracts text from plain text files (.txt).
    """
    try:
        content = uploaded_file.read().decode("utf-8", errors="replace")
        return content
    except Exception as e:
        raise ExtractionError(f"TXT extraction failed: {e}")


# --- Extract text from a .docx Word file ---
def extract_text_from_docx(uploaded_file):
    """
    Extracts text from Microsoft Word .docx files.
    """
    try:
        doc = docx.Document(uploaded_file)
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        raise ExtractionError(f"DOCX extraction failed: {e}")


# --- Extract text from a PDF file ---
def extract_text_from_pdf(uploaded_file):
    """
    Extracts text from PDF files using PyPDF2.
    """
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        text = []

        for page in reader.pages:
            extracted = page.extract_text()
            text.append(extracted or "")

        return "\n".join(text)
    except Exception as e:
        raise ExtractionError(f"PDF extraction failed: {e}")


# --- Clean up extracted text ---
def clean_text(text: str) -> str:
    """
    Removes null characters and trims whitespace.
    """
    cleaned = text.replace("\x00", "")
    return cleaned.strip()


# --- Main function the Streamlit app will call ---
def extract_and_clean(uploaded_file):
    """
    Validates file size, detects file type, extracts text,
    cleans it, and returns the final text.
    """
    validate_file_size(uploaded_file)

    file_type = uploaded_file.type

    if file_type == "text/plain":
        raw = extract_text_from_txt(uploaded_file)

    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        raw = extract_text_from_docx(uploaded_file)

    elif file_type == "application/pdf":
        raw = extract_text_from_pdf(uploaded_file)

    else:
        raise ExtractionError(f"Unsupported file type: {file_type}")

    return clean_text(raw)
