"""
Stores the candidate's target company, role, and resume text so it
persists across separate `python main.py` runs — same reasoning as
planner.py's old rotation counter, but for profile info instead of
scores. Deliberately its own file: unrelated to question_cache.py
(question storage) or session_store.py (score history).
"""

import json
from pathlib import Path
from typing import Optional, TypedDict

_PROFILE_PATH = Path(__file__).parent.parent / "data" / "candidate_profile.json"


class CandidateProfile(TypedDict):
    company: str
    role: str
    resume_text: str


def get_profile() -> Optional[CandidateProfile]:
    if not _PROFILE_PATH.exists():
        return None
    return json.loads(_PROFILE_PATH.read_text())


def set_profile(company: str, role: str, resume_text: str) -> None:
    _PROFILE_PATH.parent.mkdir(exist_ok=True)
    _PROFILE_PATH.write_text(
        json.dumps({"company": company, "role": role, "resume_text": resume_text})
    )