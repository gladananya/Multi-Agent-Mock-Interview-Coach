# """
# Question cache: stores questions we've already fetched (from Codeforces
# or, later, live web search) so repeated topic/difficulty requests don't
# re-hit the network every time.

# Deliberately holds ONLY question data — no scores, no session history.
# Phase 6's session_store.py owns all score/performance tracking, so this
# file can be reused as-is even if session memory's schema changes later.
# """

# import sqlite3
# from pathlib import Path

# _DB_PATH = Path(__file__).parent.parent / "data" / "question_cache.db"


# def _get_conn():
#     _DB_PATH.parent.mkdir(exist_ok=True)
#     conn = sqlite3.connect(_DB_PATH)
#     conn.execute(
#         """
#         CREATE TABLE IF NOT EXISTS questions (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             topic TEXT NOT NULL,
#             difficulty TEXT NOT NULL,
#             question_text TEXT NOT NULL,
#             source TEXT NOT NULL,
#             times_used INTEGER DEFAULT 0
#         )
#         """
#     )
#     conn.commit()
#     return conn


# def get_cached_question(topic: str, difficulty: str) -> str | None:
#     """Returns a cached question for this topic/difficulty, preferring
#     the least-used one so the same question isn't repeated too often.
#     Returns None on a cache miss."""
#     conn = _get_conn()
#     row = conn.execute(
#         """
#         SELECT id, question_text FROM questions
#         WHERE topic = ? AND difficulty = ?
#         ORDER BY times_used ASC LIMIT 1
#         """,
#         (topic, difficulty),
#     ).fetchone()

#     if row is None:
#         conn.close()
#         return None

#     question_id, question_text = row
#     conn.execute(
#         "UPDATE questions SET times_used = times_used + 1 WHERE id = ?",
#         (question_id,),
#     )
#     conn.commit()
#     conn.close()
#     return question_text


# def store_question(topic: str, difficulty: str, question_text: str, source: str) -> None:
#     conn = _get_conn()
#     conn.execute(
#         """
#         INSERT INTO questions (topic, difficulty, question_text, source, times_used)
#         VALUES (?, ?, ?, ?, 0)
#         """,
#         (topic, difficulty, question_text, source),
#     )
#     conn.commit()
#     conn.close()
"""
Question cache: stores questions we've already fetched (from Codeforces
or live web search) so repeated requests don't re-hit the network.

Phase 9: added optional company/role columns. DSA questions from
Codeforces aren't company-specific (no public company-tagging exists
without scraping), so they're cached under company=None/role=None as
before. Behavioral questions ARE personalized per company/role, so
they're cached per (topic, difficulty, company, role) — a "Google SDE"
question and an "Amazon PM" question are stored separately and never
served to the wrong context.

Deliberately holds ONLY question data — no scores, no session history.
Phase 6's session_store.py owns all score/performance tracking.
"""

import sqlite3
from pathlib import Path
from typing import Optional

_DB_PATH = Path(__file__).parent.parent / "data" / "question_cache.db"


def _get_conn():
    _DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(_DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            company TEXT NOT NULL DEFAULT '',
            role TEXT NOT NULL DEFAULT '',
            question_text TEXT NOT NULL,
            source TEXT NOT NULL,
            times_used INTEGER DEFAULT 0
        )
        """
    )
    # migrate a pre-existing DB from earlier phases that predates these columns
    existing_columns = {row[1] for row in conn.execute("PRAGMA table_info(questions)")}
    if "company" not in existing_columns:
        conn.execute("ALTER TABLE questions ADD COLUMN company TEXT NOT NULL DEFAULT ''")
    if "role" not in existing_columns:
        conn.execute("ALTER TABLE questions ADD COLUMN role TEXT NOT NULL DEFAULT ''")
    conn.commit()
    return conn


def get_cached_question(
    topic: str, difficulty: str, company: Optional[str] = None, role: Optional[str] = None
) -> Optional[str]:
    """Returns a cached question matching topic/difficulty/company/role,
    preferring the least-used one. Returns None on a cache miss."""
    conn = _get_conn()
    row = conn.execute(
        """
        SELECT id, question_text FROM questions
        WHERE topic = ? AND difficulty = ? AND company = ? AND role = ?
        ORDER BY times_used ASC LIMIT 1
        """,
        (topic, difficulty, company or "", role or ""),
    ).fetchone()

    if row is None:
        conn.close()
        return None

    question_id, question_text = row
    conn.execute(
        "UPDATE questions SET times_used = times_used + 1 WHERE id = ?",
        (question_id,),
    )
    conn.commit()
    conn.close()
    return question_text


def store_question(
    topic: str,
    difficulty: str,
    question_text: str,
    source: str,
    company: Optional[str] = None,
    role: Optional[str] = None,
) -> None:
    conn = _get_conn()
    conn.execute(
        """
        INSERT INTO questions (topic, difficulty, company, role, question_text, source, times_used)
        VALUES (?, ?, ?, ?, ?, ?, 0)
        """,
        (topic, difficulty, company or "", role or "", question_text, source),
    )
    conn.commit()
    conn.close()