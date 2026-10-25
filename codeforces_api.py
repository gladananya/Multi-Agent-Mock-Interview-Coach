"""
Pulls real DSA problems from Codeforces' official public API (free,
no key needed, no scraping). We only get metadata back (name, tags,
rating, link) — not the full problem statement — so the Interviewer
points the candidate to the link and asks them to explain their
approach, same as a real interviewer sharing a doc link.

The full problem set (~10k problems) is fetched once and cached in
memory for the process lifetime, so only the first call per run hits
the network.
"""

import random
import requests

_CACHE = None

_TAG_MAP = {
    "arrays": "arrays",
    "graphs": "graphs",
    "dynamic programming": "dp",
}

_DIFFICULTY_RANGES = {
    "easy": (800, 1100),
    "medium": (1200, 1600),
    "hard": (1700, 2200),
}


def _load_problems():
    global _CACHE
    if _CACHE is None:
        resp = requests.get(
            "https://codeforces.com/api/problemset.problems", timeout=10
        )
        resp.raise_for_status()
        _CACHE = resp.json()["result"]["problems"]
    return _CACHE


def get_problem(topic: str, difficulty: str) -> dict:
    """Raises on network failure or if no matching problem exists —
    the caller (interviewer.py) is responsible for falling back."""
    problems = _load_problems()
    tag = _TAG_MAP.get(topic)
    lo, hi = _DIFFICULTY_RANGES.get(difficulty, (800, 1600))

    candidates = [
        p for p in problems
        if tag in p.get("tags", []) and p.get("rating") and lo <= p["rating"] <= hi
    ]
    if not candidates:
        # relax the tag filter rather than fail outright
        candidates = [
            p for p in problems if p.get("rating") and lo <= p["rating"] <= hi
        ]
    if not candidates:
        raise ValueError(f"No Codeforces problem found for {topic}/{difficulty}")

    problem = random.choice(candidates)
    return {
        "name": problem["name"],
        "rating": problem.get("rating"),
        "tags": problem.get("tags", []),
        "url": f"https://codeforces.com/problemset/problem/{problem['contestId']}/{problem['index']}",
    }
