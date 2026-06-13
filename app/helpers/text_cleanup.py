import ftfy
import re

#used ftfy for text cleanup

def clean_text(text: str) -> str:
    text = ftfy.fix_text(text)
    text = text.strip()
    text = normalize_whitespace(text)
    text = fix_broken_lines(text)
    text = remove_empty_blocks(text)
    text = remove_headers_footers(text)
    text = format_metadata(text)
    return text


def normalize_whitespace(text: str) -> str:
    # Replace multiple spaces with single space
    text = " ".join(text.split())

    # Replace multiple newlines with double newline (paragraph breaks)
    text = "\n\n".join(paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip())
    return text

def fix_broken_lines(text: str) -> str:
    # Fix words split with hyphen at end of line: "exam-\nple" → "example"
    text = text.replace("-\n", "")
    # Fix words broken without hyphen: "exam \nple" → "example"
    lines = text.split("\n")
    fixed = []
    for i, line in enumerate(lines):
        if line and i > 0 and not line[0].isupper() and fixed:
            # Likely a continuation; append to previous line
            fixed[-1] += line
        else:
            fixed.append(line)
    return "\n".join(fixed)

def remove_empty_blocks(text: str) -> str:
    # Remove lines with only whitespace
    lines = [line for line in text.split("\n") if line.strip()]
    return "\n".join(lines)

def remove_headers_footers(text: str) -> str:
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        # Skip lines that are only page numbers, dates, or common headers
        if line.strip() and not (
            line.strip().isdigit() or  # Just numbers (page numbers)
            len(line.strip()) < 5 or  # Very short lines (often footers)
            any(keyword in line.lower() for keyword in ["page ", "date:", "copyright"])
        ):
            cleaned.append(line)
    return "\n".join(cleaned)


def format_metadata(text: str) -> str:
    # Standardize author: "By John" → "Author: John"
    text = re.sub(r"^By\s+(.+)$", r"Author: \1", text, flags=re.MULTILINE)
    # Standardize date format: "Dec 25, 2024" stays, "12/25/2024" → standardized
    text = re.sub(r"(\d{1,2})/(\d{1,2})/(\d{4})", r"\3-\1-\2", text)
    return text
