"""
Removes filler words from a raw transcript before it's used for content
scoring. The Evaluator's content-correctness prompt should never see
"um"s and "like"s — it should grade exactly as it would grade typed
text. The RAW transcript (with fillers intact) is kept separately in
state["raw_transcript"] for the communication scorer, which needs the
fillers to actually measure the filler rate.
"""

import re

_FILLER_PATTERN = re.compile(
    r"\b(um+|uh+|like|you know|i mean|basically|actually|sort of|kind of)\b",
    re.IGNORECASE,
)


def clean_transcript(raw_text: str) -> str:
    cleaned = _FILLER_PATTERN.sub("", raw_text)
    cleaned = re.sub(r"\s*,\s*,", ",", cleaned)   # collapse double commas left by removal
    cleaned = re.sub(r",\s*\.", ".", cleaned)     # ", ." -> "."
    cleaned = re.sub(r"^\s*,\s*", "", cleaned)    # leading comma
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned