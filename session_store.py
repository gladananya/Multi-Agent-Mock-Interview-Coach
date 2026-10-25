# 
"""
Tracks every attempt (topic, difficulty, score) across sessions in
SQLite. This is the real replacement for Phase 1-5's throwaway
topic_rotation.json counter — the Planner reads this to find weak
topics and adapt difficulty, instead of just cycling blindly.

Deliberately holds ONLY performance data — no question text, which
stays owned by memory/question_cache.py.
"""

import sqlite3
import datetime
from pathlib import Path

_DB_PATH = Path(__file__).parent.parent / "data" / "session_store.db"


def _get_conn():
    _DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(_DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            score REAL,
            timestamp TEXT NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def log_attempt(topic: str, difficulty: str, score: float | None) -> None:
    conn = _get_conn()
    conn.execute(
        "INSERT INTO attempts (topic, difficulty, score, timestamp) VALUES (?, ?, ?, ?)",
        (topic, difficulty, score, datetime.datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def get_topic_performance() -> dict:
    """Returns {topic: {avg_score, last_score, last_difficulty, attempts}}
    for every topic that has at least one scored attempt. Topics never
    attempted, or attempts with no score (e.g. a crashed run), don't
    appear here."""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT topic, difficulty, score FROM attempts WHERE score IS NOT NULL ORDER BY id ASC"
    ).fetchall()
    conn.close()

    by_topic: dict[str, dict] = {}
    for topic, difficulty, score in rows:
        entry = by_topic.setdefault(topic, {"scores": [], "last_difficulty": difficulty})
        entry["scores"].append(score)
        entry["last_difficulty"] = difficulty

    return {
        topic: {
            "avg_score": sum(data["scores"]) / len(data["scores"]),
            "last_score": data["scores"][-1],
            "last_difficulty": data["last_difficulty"],
            "attempts": len(data["scores"]),
        }
        for topic, data in by_topic.items()
    }


def get_attempt_history(limit: int = 200) -> list[dict]:
    """Most recent scored attempts, oldest first — feeds the UI's progress
    chart. Read-only; the Planner still uses get_topic_performance()."""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT topic, difficulty, score, timestamp FROM attempts "
        "WHERE score IS NOT NULL ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [
        {"topic": t, "difficulty": d, "score": sc, "timestamp": ts}
        for t, d, sc, ts in reversed(rows)
    ]