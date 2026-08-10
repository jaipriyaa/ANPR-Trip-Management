import re


INDIAN_PLATE_PATTERNS = [
    r"^[A-Z]{2}\d{1,2}[A-Z]{1,2}\d{4}$",
    r"^[A-Z]{2}\d{1,2}[A-Z]{1,2}\d{3,4}$",
    r"^[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}$",
]

INDIAN_STATE_CODES = {
    "AP", "AR", "AS", "BR", "CG", "DL", "GA", "GJ", "HR", "HP",
    "JH", "JK", "KA", "KL", "LD", "MH", "ML", "MN", "MP", "MZ",
    "NL", "OD", "PB", "PY", "RJ", "SK", "TN", "TR", "TS", "UK",
    "UP", "WB", "AN", "CH", "DN", "DD", "LA",
}


def clean_plate_text(raw: str) -> str:
    cleaned = re.sub(r"[^A-Z0-9]", "", raw.upper())
    return cleaned


def is_valid_indian_plate(plate_text: str) -> bool:
    cleaned = clean_plate_text(plate_text)
    for pattern in INDIAN_PLATE_PATTERNS:
        if re.match(pattern, cleaned):
            state_code = cleaned[:2]
            if state_code in INDIAN_STATE_CODES:
                return True
    return False


def validate_and_correct(plate_text: str) -> tuple:
    cleaned = clean_plate_text(plate_text)
    is_valid = is_valid_indian_plate(cleaned)
    return cleaned, is_valid
