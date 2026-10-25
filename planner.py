# """
# Planner agent.

# Phase 6: replaces the throwaway topic_rotation.json counter with real
# adaptive selection based on memory/session_store.py.

# Topic selection: any topic never attempted gets priority (explore
# before you exploit). Once every topic has at least one scored
# attempt, the weakest one (lowest average score) is picked next.

# Difficulty selection: starts at each topic's base difficulty. Once a
# topic has 2+ attempts, a strong average (>=8) bumps difficulty up one
# level, a weak average (<=4) drops it one level, otherwise it holds.
# """

# from state import InterviewState
# from memory.session_store import get_topic_performance

# _TOPICS = ["arrays", "graphs", "dynamic programming", "behavioral"]

# _BASE_DIFFICULTY = {
#     "arrays": "easy",
#     "graphs": "medium",
#     "dynamic programming": "medium",
#     "behavioral": "medium",
# }

# _DIFFICULTY_ORDER = ["easy", "medium", "hard"]


# def _pick_topic(performance: dict) -> str:
#     untried = [t for t in _TOPICS if t not in performance]
#     if untried:
#         return untried[0]
#     return min(performance.items(), key=lambda kv: kv[1]["avg_score"])[0]


# def _pick_difficulty(topic: str, performance: dict) -> str:
#     base = _BASE_DIFFICULTY[topic]
#     data = performance.get(topic)

#     if data is None or data["attempts"] < 2:
#         return base

#     idx = _DIFFICULTY_ORDER.index(
#         data["last_difficulty"] if data["last_difficulty"] in _DIFFICULTY_ORDER else base
#     )
#     if data["avg_score"] >= 8 and idx < len(_DIFFICULTY_ORDER) - 1:
#         idx += 1
#     elif data["avg_score"] <= 4 and idx > 0:
#         idx -= 1

#     return _DIFFICULTY_ORDER[idx]


# def planner_node(state: InterviewState) -> InterviewState:
#     performance = get_topic_performance()
#     topic = _pick_topic(performance)
#     difficulty = _pick_difficulty(topic, performance)

#     state["question_topic"] = topic
#     state["question_difficulty"] = difficulty
#     state["topic_history"] = state["topic_history"] + [topic]
#     return state
"""
Planner agent.

Phase 6: adaptive selection based on memory/session_store.py — any
topic never attempted gets priority; once everything's been tried, the
weakest one (lowest average score) is picked next. Difficulty starts
at each topic's base level and moves up/down based on recent average.

Phase 11: planner_node now respects a topic that's already been set in
state before it runs — main.py's round orchestration (Technical /
Behavioral rounds) sets question_topic explicitly per question, and
the Planner should only adapt difficulty for it, not override the
topic choice. When no topic is pre-set (state["question_topic"] is
None), it picks one itself exactly as before — this keeps the old
single-question flow working unchanged.

pick_topic_from() is exposed publicly so main.py can reuse the same
untried-first/weakest-average logic restricted to just the DSA topics,
for the "which DSA question this technical round" decision.
"""

from typing import Optional
from state import InterviewState
from memory.session_store import get_topic_performance

_TOPICS = ["arrays", "graphs", "dynamic programming", "behavioral"]

_BASE_DIFFICULTY = {
    "arrays": "easy",
    "graphs": "medium",
    "dynamic programming": "medium",
    "behavioral": "medium",
}

_DIFFICULTY_ORDER = ["easy", "medium", "hard"]


def pick_topic_from(candidates: list[str], performance: Optional[dict] = None) -> str:
    if performance is None:
        performance = get_topic_performance()
    untried = [t for t in candidates if t not in performance]
    if untried:
        return untried[0]
    return min(
        ((t, performance[t]) for t in candidates if t in performance),
        key=lambda kv: kv[1]["avg_score"],
    )[0]


def _pick_difficulty(topic: str, performance: dict) -> str:
    base = _BASE_DIFFICULTY.get(topic, "medium")
    data = performance.get(topic)

    if data is None or data["attempts"] < 2:
        return base

    idx = _DIFFICULTY_ORDER.index(
        data["last_difficulty"] if data["last_difficulty"] in _DIFFICULTY_ORDER else base
    )
    if data["avg_score"] >= 8 and idx < len(_DIFFICULTY_ORDER) - 1:
        idx += 1
    elif data["avg_score"] <= 4 and idx > 0:
        idx -= 1

    return _DIFFICULTY_ORDER[idx]


def planner_node(state: InterviewState) -> InterviewState:
    performance = get_topic_performance()
    topic = state.get("question_topic") or pick_topic_from(_TOPICS, performance)
    difficulty = _pick_difficulty(topic, performance)

    state["question_topic"] = topic
    state["question_difficulty"] = difficulty
    state["topic_history"] = state["topic_history"] + [topic]
    return state