"""
Tracks resume-based questions already asked, across separate `python
main.py` runs, so the resume-question generator (tools/resume_question.py)
doesn't keep landing on the same salient resume detail every Technical
round. Keeps only the most recent N so the file doesn't grow unbounded
and so very old questions eventually cycle back into eligibility.
"""

import json
from pathlib import Path

_PATH = Path(__file__).parent.parent / "data" / "resume_questions_asked.json"
_MAX_HISTORY = 15


def get_asked_resume_questions() -> list[str]:
    if not _PATH.exists():
        return []
    return json.loads(_PATH.read_text())


def add_asked_resume_question(question: str) -> None:
    history = get_asked_resume_questions()
    history.append(question)
    history = history[-_MAX_HISTORY:]

    _PATH.parent.mkdir(exist_ok=True)
    _PATH.write_text(json.dumps(history))