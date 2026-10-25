"""
Scores communication quality (filler-word rate, speaking pace) from the
RAW transcript + duration. Deliberately deterministic, not LLM-based —
this is a hard, checkable metric (word counts, timing), and computing
it in code means it's actually testable without a network call, unlike
an LLM-graded version would be.

This never touches content_score's inputs and content_score never
touches this — a rambly-but-correct answer isn't penalized here for
correctness, and a smooth-but-wrong one isn't rewarded for delivery.
"""

import re

_FILLER_PATTERN = re.compile(
    r"\b(um+|uh+|like|you know|i mean|basically|actually|sort of|kind of)\b",
    re.IGNORECASE,
)

_IDEAL_WPM_RANGE = (90, 190)
_MAX_FILLER_PENALTY = 5.0
_FILLER_PENALTY_PER_HIT = 0.5
_PACE_PENALTY = 2.0


def score_communication(raw_transcript: str, duration_seconds: float) -> tuple[float, str]:
    word_count = len(raw_transcript.split())
    filler_count = len(_FILLER_PATTERN.findall(raw_transcript))
    wpm = (word_count / duration_seconds * 60) if duration_seconds > 0 else 0.0

    score = 10.0
    score -= min(filler_count * _FILLER_PENALTY_PER_HIT, _MAX_FILLER_PENALTY)

    pace_note = "good pace"
    if wpm and wpm < _IDEAL_WPM_RANGE[0]:
        score -= _PACE_PENALTY
        pace_note = "a bit slow"
    elif wpm and wpm > _IDEAL_WPM_RANGE[1]:
        score -= _PACE_PENALTY
        pace_note = "a bit fast"

    score = max(0.0, round(score, 1))
    feedback = f"{filler_count} filler word(s), ~{wpm:.0f} words/min ({pace_note})."
    return score, feedback