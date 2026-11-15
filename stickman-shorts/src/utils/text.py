"""Text helpers: Vietnamese-safe text handling.

Rules (from the project research):
- ALWAYS normalize to NFC before rendering (macOS/AI tools sometimes emit
  NFD, where a diacritic is a separate code point and drifts off the vowel).
- NEVER use LaTeX/Tex for Vietnamese text; Manim Text (Pango) only.
- Split long lines so a card never overflows the 9-unit-wide frame.
"""

from __future__ import annotations

import unicodedata

VIETNAMESE_TEST = "Tâm sự người que — Ăn cơm chưa? Đi làm muộn, ồ ạt, ứ ự, ỹ, ỳ, ỵ."
VIETNAMESE_MARKS = "ăâêôơưđáàảãạấầẩẫậớờởỡợứừửữựỳỵỷỹ"


def normalize_text(text: str) -> str:
    """NFC-normalize so combining diacritics stay glued to their vowel."""
    return unicodedata.normalize("NFC", text)


def split_text(text: str, max_chars: int = 30) -> list[str]:
    """Greedy word wrap: each line <= ``max_chars`` characters."""
    words = normalize_text(text).split()
    lines: list[str] = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 <= max_chars:
            current = f"{current} {word}".strip()
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def check_vietnamese_coverage(text: str) -> list[str]:
    """Return any Vietnamese characters in ``text`` that are NOT in the
    test string — a quick smoke check that a font covers the text."""
    return sorted({ch for ch in text if ch in VIETNAMESE_MARKS} - set(VIETNAMESE_MARKS))
