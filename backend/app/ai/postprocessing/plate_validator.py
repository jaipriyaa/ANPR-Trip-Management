import re
from typing import Dict, List, Optional, Tuple

from app.ai import config

INDIAN_PLATE_PATTERNS = [
    (r"^([A-Z]{2})(\d{1,2})([A-Z]{1,3})(\d{3,4})$", "Standard"),
    (r"^([A-Z]{2})(\d{2})([A-Z]{1,3})(\d{1,4}[A-Z]?)$", "Temporary/Dealer"),
    (r"^([A-Z]{2})(\d{1,2})([A-Z]{1,2})(\d{3,4})$", "Standard"),
    (r"^([A-Z]{2})(\d{2})([A-Z]{1,2})(\d{3})$", "OldFormat"),
    (r"^(BH)(\d{1,2})([A-Z]{1,2})(\d{4})$", "Bharat"),
    (r"^(CD|CC|CG|UN)(\d{1,4})$", "Diplomat"),
    (r"^(HR)(\d{1,2})([A-Z]{0,2})(\d{4})$", "Haryana"),
    (r"^(DL)(\d{1,2})([A-Z]{1,3})(\d{4})$", "Delhi"),
    (r"^(\d{2})([A-Z]{2,3})(\d{3,4})$", "Commercial/International"),
    (r"^([A-Z]{2})(\d{2})([A-Z]{3})(\d{3,4})([A-Z]?)$", "Commercial/Trade"),
]

STATE_CODES = {
    "AP", "AR", "AS", "BR", "CG", "DL", "GA", "GJ", "HR", "HP",
    "JH", "JK", "KA", "KL", "LD", "MH", "ML", "MN", "MP", "MZ",
    "NL", "OD", "OR", "PB", "PY", "RJ", "SK", "TN", "TR", "TS", "UK",
    "UP", "WB", "AN", "CH", "DN", "DD", "LA",
}

BHARAT_STATES = {"BH"}

CHAR_CONFUSIONS: Dict[str, List[str]] = {
    "0": ["O", "Q", "D", "U"],
    "O": ["0", "Q", "D", "U"],
    "1": ["I", "L", "T"],
    "I": ["1", "L", "T"],
    "2": ["Z"],
    "Z": ["2"],
    "5": ["S"],
    "S": ["5"],
    "6": ["G", "C"],
    "G": ["6", "C"],
    "8": ["B", "3"],
    "B": ["8", "3"],
}


CONTAINER_BRANDING_BLACKLIST = set(getattr(config, "BRANDING_BLACKLIST", [
    "GOODS", "CARRIER", "LOGISTICS", "ASHOK", "LEYLAND", "TATA",
    "BHARATBENZ", "EICHER", "VOLVO", "SCANIA", "TRANSPORT", "TRUCK",
    "BUS", "CONTAINER", "PUBLIC", "PERMIT", "SPEED", "ALLINDIA",
    "SAFETY", "FIRST", "SALES", "INDIA", "SERVICE", "REPAIR"
]))


class IndianPlateValidator:

    def __init__(self):
        self.patterns = INDIAN_PLATE_PATTERNS
        self.state_codes = STATE_CODES
        self.char_confusions = CHAR_CONFUSIONS
        self.blacklist = set(getattr(config, "BRANDING_BLACKLIST", CONTAINER_BRANDING_BLACKLIST))

    def clean(self, raw: str) -> str:
        return re.sub(r"[^A-Z0-9]", "", raw.upper())

    def is_blacklisted_text(self, raw: str) -> bool:
        up = raw.upper()
        return any(w in up for w in self.blacklist)

    def validate(self, plate_text: str) -> Tuple[bool, str, Optional[dict]]:
        if self.is_blacklisted_text(plate_text):
            return False, self.clean(plate_text), None

        cleaned = self.clean(plate_text)
        if len(cleaned) < config.VALIDATION_MIN_LENGTH or len(cleaned) > config.VALIDATION_MAX_LENGTH:
            return False, cleaned, None


        for pattern, fmt_name in self.patterns:
            match = re.match(pattern, cleaned)
            if match:
                state = match.group(1) if match.groups() else ""
                if state in self.state_codes or state in BHARAT_STATES or fmt_name in ["Commercial/International", "Commercial/Trade"]:
                    return True, cleaned, {
                        "format": fmt_name,
                        "state": state,
                        "groups": list(match.groups()),
                    }

        return False, cleaned, None


    def correct(self, raw: str) -> str:
        cleaned = self.clean(raw)
        if not cleaned:
            return cleaned

        is_valid, validated, info = self.validate(cleaned)
        if is_valid:
            return validated

        candidates = self._generate_candidates(cleaned)

        for candidate in candidates:
            is_valid, _, info = self.validate(candidate)
            if is_valid:
                return candidate

        return cleaned

    def correct_with_confidence(self, raw: str, ocr_confidence: float) -> dict:
        cleaned = self.clean(raw)
        is_valid, validated, info = self.validate(cleaned)

        if is_valid:
            return {
                "plate_text": validated,
                "original_text": cleaned,
                "is_valid": True,
                "confidence": ocr_confidence,
                "corrections": [],
            }

        candidates = self._generate_candidates(cleaned)
        best_candidate = None
        best_conf = 0.0

        for candidate in candidates:
            is_valid, _, info = self.validate(candidate)
            if is_valid:
                corrections = self._get_corrections(cleaned, candidate)
                correction_count = len(corrections)
                confidence_penalty = 1.0 - (correction_count * 0.1)
                adjusted_conf = min(1.0, ocr_confidence * confidence_penalty)

                if adjusted_conf > best_conf:
                    best_candidate = {
                        "plate_text": candidate,
                        "original_text": cleaned,
                        "is_valid": True,
                        "confidence": adjusted_conf,
                        "corrections": corrections,
                    }
                    best_conf = adjusted_conf

        if best_candidate:
            return best_candidate

        return {
            "plate_text": cleaned,
            "original_text": cleaned,
            "is_valid": is_valid,
            "confidence": ocr_confidence,
            "corrections": [],
        }

    def _generate_candidates(self, text: str) -> List[str]:
        candidates = set()
        candidates.add(text)

        # Handle 2-line plate OCR order inversion (e.g. "4132MHOZDT" -> "MHOZDT4132")
        for sc in self.state_codes:
            pos = text.find(sc)
            if pos > 0:
                reordered = text[pos:] + text[:pos]
                candidates.add(reordered)

        base_list = list(candidates)
        for base_str in base_list:
            chars = list(base_str)
            self._generate_candidates_bounded(chars, 0, candidates)
            if len(candidates) >= 100:
                break

        return list(candidates)[:100]

    def _generate_candidates_bounded(self, chars: list, idx: int, candidates: set):
        if len(candidates) >= 100:
            return
        if idx >= len(chars):
            candidates.add("".join(chars))
            return

        char = chars[idx]
        if char in self.char_confusions:
            for replacement in self.char_confusions[char]:
                chars[idx] = replacement
                self._generate_candidates_bounded(chars, idx + 1, candidates)
                if len(candidates) >= 100:
                    return
            chars[idx] = char

        self._generate_candidates_bounded(chars, idx + 1, candidates)

    def _get_corrections(self, original: str, corrected: str) -> list:
        corrections = []
        for i, (o, c) in enumerate(zip(original, corrected)):
            if o != c:
                corrections.append({
                    "position": i,
                    "original": o,
                    "corrected": c,
                })
        for i in range(len(corrected), len(original)):
            corrections.append({
                "position": i,
                "original": original[i],
                "corrected": "",
                "action": "deleted",
            })
        return corrections
