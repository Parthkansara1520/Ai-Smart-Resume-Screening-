"""
parser.py
Provides functionality to extract text from PDF and DOCX files, clean extracted text,
and parse candidate contact information (email, phone number), estimated professional
experience, and detected education levels.
Handles corrupted, empty, or scanned/unreadable documents gracefully.
"""

import io
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

# Ensure project root is in sys.path
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import docx
from pypdf import PdfReader


def extract_text_from_pdf(file: Any) -> str:
    """
    Extracts text from a PDF file using pypdf.
    Supports a file path string, Path object, or file-like / BytesIO stream.
    Gracefully handles encrypted, empty, or corrupted files.
    """
    try:
        if hasattr(file, "seek"):
            file.seek(0)
        reader = PdfReader(file)
        text_parts = []
        for page in reader.pages:
            try:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            except Exception:
                continue
        return "\n".join(text_parts)
    except Exception:
        return ""


def extract_text_from_docx(file: Any) -> str:
    """
    Extracts text from a DOCX file using python-docx.
    Extracts from both body paragraphs and table cells.
    Supports a file path string, Path object, or file-like / BytesIO stream.
    Gracefully handles corrupted or malformed documents.
    """
    try:
        if hasattr(file, "seek"):
            file.seek(0)
        doc = docx.Document(file)
        text_parts = []

        # Extract text from paragraphs
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if text:
                text_parts.append(text)

        # Extract text from tables (often used for skill grids and work experience)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    cell_text = cell.text.strip()
                    if cell_text:
                        text_parts.append(cell_text)

        return "\n".join(text_parts)
    except Exception:
        return ""


def extract_email(text: str) -> str:
    """
    Extracts the first valid email address found in the text using regex.
    Returns 'Not Found' if missing or unreadable.
    """
    if not text:
        return "Not Found"
    email_pattern = re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    )
    match = email_pattern.search(text)
    return match.group(0) if match else "Not Found"


def extract_phone(text: str) -> str:
    """
    Extracts the first valid phone number found in the text using regex.
    Handles international formats, hyphens, dots, parentheses, and spaces.
    Validates digit count between 10 and 15 digits (to avoid matching dates like 2020-2024).
    Returns 'Not Found' if missing or unreadable.
    """
    if not text:
        return "Not Found"

    # Pattern 1: Standard structured formats like +1 (555) 123-4567 or 123-456-7890
    std_pattern = re.compile(
        r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    )
    for match in std_pattern.finditer(text):
        cand = match.group(0).strip()
        digits = re.sub(r'\D', '', cand)
        if 10 <= len(digits) <= 15:
            return cand

    # Pattern 2: Broader international formats like +91 9876543210 or +44 20 7946 0958
    broader_pattern = re.compile(
        r'(?:\+?\d{1,4}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,5}[-.\s]?\d{3,5}'
    )
    for match in broader_pattern.finditer(text):
        cand = match.group(0).strip()
        digits = re.sub(r'\D', '', cand)
        if 10 <= len(digits) <= 15:
            return cand

    return "Not Found"


def extract_experience_years(text: str) -> Tuple[float, str]:
    """
    Extracts estimated years of professional experience from resume text.
    Combines explicit mentions (e.g., '5+ years of experience') and date range analysis.
    Returns (years_float, years_display_string).
    """
    if not text:
        return 0.0, "Not Specified"

    # 1. Direct explicit mentions like '5+ years of experience', '3 years experience'
    explicit_pattern = re.compile(
        r'(?:(?:over|more than|approx\.?|about)\s+)?(\d+(?:\.\d+)?)\+?\s*(?:to\s*\d+\s*)?(?:years?|yrs?)(?:\s+(?:of\s+)?(?:experience|exp|background|expertise|\w+\s+experience))',
        re.IGNORECASE
    )
    direct_matches = explicit_pattern.findall(text)
    direct_years = [float(y) for y in direct_matches if 0 < float(y) <= 40]

    # 2. Employment date ranges (e.g., '2019 - 2022', '2021 - Present')
    range_pattern = re.compile(
        r'\b(20\d{2}|19\d{2})\s*(?:-|–|—|to)\s*(20\d{2}|19\d{2}|present|current)\b',
        re.IGNORECASE
    )
    range_matches = range_pattern.findall(text)
    current_year = 2026
    range_spans = []
    for start, end in range_matches:
        sy = int(start)
        ey = current_year if end.lower() in ['present', 'current'] else int(end)
        diff = ey - sy
        if 0 < diff <= 35:
            range_spans.append(diff)

    estimated = 0.0
    if direct_years:
        estimated = max(direct_years)
    elif range_spans:
        # Sum of distinct job durations (capped sensibly)
        estimated = min(35.0, float(sum(range_spans)))

    if estimated > 0:
        display_str = f"{int(estimated) if estimated.is_integer() else estimated}+ yrs"
        return estimated, display_str

    return 0.0, "Not Specified"


def extract_education(text: str) -> str:
    """
    Detects key education degrees and qualifications from resume text.
    Handles Ph.D., M.Tech, M.S., MCA, MBA, B.Tech, B.S., BCA, etc.
    """
    if not text:
        return "Not Specified"

    degree_patterns = [
        ("Ph.D. / Doctorate", r'\b(?:ph\.?d\.?|doctorate|doctoral)\b'),
        ("M.Tech / M.E.", r'\b(?:m\.?\s*tech|m\.?\s*e\.?|master of technology|master of engineering)\b'),
        ("M.S. / M.Sc", r'\b(?:m\.?\s*s\.?|m\.?\s*sc\.?|master of science)\b'),
        ("MCA", r'\b(?:mca|master of computer applications)\b'),
        ("MBA", r'\b(?:mba|master of business administration)\b'),
        ("B.Tech / B.E.", r'\b(?:b\.?\s*tech|b\.?\s*e\.?|bachelor of technology|bachelor of engineering)\b'),
        ("B.S. / B.Sc", r'\b(?:b\.?\s*s\.?|b\.?\s*sc\.?|bachelor of science)\b'),
        ("BCA", r'\b(?:bca|bachelor of computer applications)\b'),
        ("BBA / B.Com", r'\b(?:bba|b\.?\s*com|bachelor of business administration|bachelor of commerce)\b'),
        ("Associate Degree", r'\b(?:associate degree|associate of (?:science|arts|applied science))\b'),
        ("Diploma", r'\b(?:diploma|polytechnic)\b')
    ]

    found_degrees = []
    for label, pat in degree_patterns:
        if re.search(pat, text, re.IGNORECASE):
            if label not in found_degrees:
                found_degrees.append(label)

    return ", ".join(found_degrees) if found_degrees else "Not Specified"


def parse_resume(uploaded_file: Any) -> Dict[str, Any]:
    """
    Parses a resume file (.pdf or .docx), cleans the text content, and extracts
    candidate contact info, estimated years of experience, and detected education.

    Detects and handles empty or scanned/unreadable documents cleanly.

    Returns:
        dict: {
            "filename": str,
            "text": str,
            "email": str,
            "phone": str,
            "experience_years": float,
            "experience_display": str,
            "education": str,
            "is_empty": bool,
            "word_count": int,
            "status_note": str
        }
    """
    # Determine filename
    if hasattr(uploaded_file, "name"):
        filename = str(uploaded_file.name)
    elif isinstance(uploaded_file, (str, Path)):
        filename = Path(uploaded_file).name
    else:
        filename = "uploaded_document"

    try:
        # Normalize file-like object to a seekable BytesIO if needed
        if hasattr(uploaded_file, "read"):
            if hasattr(uploaded_file, "seek"):
                uploaded_file.seek(0)
            file_bytes = uploaded_file.read()
            if hasattr(uploaded_file, "seek"):
                uploaded_file.seek(0)
            file_stream = io.BytesIO(file_bytes)
        else:
            file_stream = uploaded_file

        # Detect extension and extract text
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".pdf":
            raw_text = extract_text_from_pdf(file_stream)
        elif ext in [".docx", ".doc"]:
            raw_text = extract_text_from_docx(file_stream)
        else:
            raw_text = ""

        # Clean extra whitespace and newlines
        cleaned_text = re.sub(r'[ \t]+', ' ', raw_text)
        cleaned_text = re.sub(r'(\r?\n\s*){2,}', '\n\n', cleaned_text).strip()

        word_count = len(cleaned_text.split())
        is_empty = (word_count == 0)

        if is_empty:
            status_note = "Unreadable or scanned document (no extractable text layer detected)."
        elif word_count < 15:
            status_note = "Very low text content detected."
        else:
            status_note = "Successfully parsed."

        # Extract contact info
        email = extract_email(cleaned_text)
        phone = extract_phone(cleaned_text)

        # Extract experience & education
        if not is_empty:
            experience_years, experience_display = extract_experience_years(cleaned_text)
            education = extract_education(cleaned_text)
        else:
            experience_years, experience_display = 0.0, "Not Specified"
            education = "Not Specified"

        return {
            "filename": filename,
            "text": cleaned_text,
            "email": email,
            "phone": phone,
            "experience_years": experience_years,
            "experience_display": experience_display,
            "education": education,
            "is_empty": is_empty,
            "word_count": word_count,
            "status_note": status_note
        }

    except Exception as e:
        return {
            "filename": filename,
            "text": "",
            "email": "Not Found",
            "phone": "Not Found",
            "experience_years": 0.0,
            "experience_display": "Not Specified",
            "education": "Not Specified",
            "is_empty": True,
            "word_count": 0,
            "status_note": f"Error during parsing: {str(e)}"
        }
