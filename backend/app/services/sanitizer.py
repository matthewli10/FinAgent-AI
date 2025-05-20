import re

def sanitize_transcript(text: str) -> str:
    """
    Cleans transcript text to avoid malformed JSON, unescaped characters, and weird formatting.
    """
    # Replace smart quotes with plain ones
    text = text.replace("“", "\"").replace("”", "\"")
    text = text.replace("‘", "'").replace("’", "'")

    # Replace curly dashes or non-breaking spaces
    text = text.replace("–", "-").replace("\u00A0", " ")

    # Remove control characters (ASCII 0-31 except newline)
    text = re.sub(r"[\x00-\x08\x0B-\x1F\x7F]", "", text)

    # Normalize excessive whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text
