"""
Everything the web UI needs that isn't a Streamlit widget.

Kept free of any `streamlit` import on purpose: the agents collect answers
with blocking input() calls (interviewer_node), which a browser UI can't
use, so this module is the non-interactive seam — plan a round, load one
question at a time, grade a submission — and app.py only draws widgets
around it. That split is also what makes the flow unit-testable without
a browser.

Round structure mirrors main.py exactly:
  Technical  -> 1 DSA question (weakest DSA topic) + 1 resume-based question
  Behavioral -> N HR-style questions, each different from the last
"""

import contextlib
import datetime
import hashlib
import io
import re
import uuid
from statistics import mean
from typing import Optional

from state import InterviewState, initial_state
from planner import planner_node, pick_topic_from
from interviewer import fetch_question, DSA_TOPICS
from evaluator import evaluator_node
from memory.session_store import get_topic_performance
from memory.asked_resume_questions import get_asked_resume_questions, add_asked_resume_question
from tools.transcript_cleaner import clean_transcript

TECHNICAL = "technical"
BEHAVIORAL = "behavioral"
LANGUAGES = ["cpp", "python", "java", "javascript"]

KIND_LABELS = {
    "dsa": "DSA question",
    "resume": "Resume-based question",
    "hr": "HR question",
}


# ---------------------------------------------------------------------------
# Round planning and question loading
# ---------------------------------------------------------------------------
def new_round(round_type: str, hr_count: int = 3) -> dict:
    if round_type == TECHNICAL:
        # sorted() so "which untried topic first" is deterministic — set
        # iteration order of strings changes between Python processes.
        dsa_topic = pick_topic_from(sorted(DSA_TOPICS), get_topic_performance())
        plan = [
            {"kind": "dsa", "topic": dsa_topic},
            {"kind": "resume", "topic": "behavioral"},
        ]
    elif round_type == BEHAVIORAL:
        plan = [{"kind": "hr", "topic": "behavioral"} for _ in range(max(1, hr_count))]
    else:
        raise ValueError(f"Unknown round type: {round_type!r}")

    return {
        # the id namespaces widget keys, so a new round never inherits the
        # previous round's typed text or code
        "id": uuid.uuid4().hex[:8],
        "type": round_type,
        "plan": plan,
        "index": 0,
        "results": [],
        "asked_this_round": [],
    }


def load_question(rnd: dict, profile: dict) -> tuple[InterviewState, list[str]]:
    """Builds the current question. Returns (state, notes) where notes are
    the status lines the backend prints ("[Served from cache]", "[Resume-
    grounded question]", fallback warnings...) so the UI can show where the
    question came from instead of hiding it in the terminal.

    Also records the question in the right "already asked" history, exactly
    as main.py does, so future rounds don't repeat it."""
    spec = rnd["plan"][rnd["index"]]
    kind = spec["kind"]

    # HR questions deliberately get an empty resume so the resume tier is
    # skipped and they're genuine HR/company-style questions.
    resume_text = "" if kind == "hr" else profile.get("resume_text", "")
    state = initial_state(
        company=profile.get("company", ""),
        role=profile.get("role", ""),
        resume_text=resume_text,
    )
    state["question_topic"] = spec["topic"]

    if kind == "dsa":
        # always a fresh fetch rather than the one cached question for this
        # topic/difficulty
        state["skip_cache"] = True
    elif kind == "resume":
        state["avoid_questions"] = get_asked_resume_questions()
    else:
        state["skip_cache"] = True
        state["avoid_questions"] = list(rnd["asked_this_round"])

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        state = planner_node(state)
        state = fetch_question(state)
    notes = [line.strip() for line in buf.getvalue().splitlines() if line.strip()]

    question = state["current_question"]
    if kind == "resume":
        add_asked_resume_question(question)
    elif kind == "hr":
        rnd["asked_this_round"].append(question)

    return state, notes


def finish_question(rnd: dict, state: InterviewState) -> bool:
    """Files a graded question into the round. Returns True when the round is done."""
    rnd["results"].append(state)
    rnd["index"] += 1
    return rnd["index"] >= len(rnd["plan"])


# ---------------------------------------------------------------------------
# Code execution and grading
# ---------------------------------------------------------------------------
def code_signature(code: str, language: str) -> str:
    """Identifies exactly what was run, so a preview run can be reused at
    submit time — and a stale one (code edited since) can be detected."""
    return hashlib.sha256(f"{language}\n{code}".encode("utf-8")).hexdigest()


def run_submission(question: str, code: str, language: str) -> tuple[Optional[dict], list[str]]:
    """Auto test-harness first (paste just your Solution class), falling back
    to a single plain run (you supply a main()). Same fallback order as the
    CLI's _maybe_run_code. Returns (sandbox_result_or_None, notes)."""
    notes: list[str] = []

    try:
        from tools.test_harness import run_test_cases
        return run_test_cases(question, code, language), notes
    except Exception as e:
        notes.append(
            f"Automated test-case grading wasn't possible ({e}), so your code was run once as a plain program instead."
        )

    try:
        from tools.sandbox import run_code
        return run_code(code, language), notes
    except Exception as e:
        notes.append(f"The sandbox couldn't run your code: {e}")
        return None, notes


def grade(
    state: InterviewState,
    *,
    answer_text: str = "",
    transcript: Optional[str] = None,
    duration: Optional[float] = None,
    code: Optional[str] = None,
    language: Optional[str] = None,
    sandbox_result: Optional[dict] = None,
    run_notes: Optional[list[str]] = None,
) -> tuple[InterviewState, list[str]]:
    """Fills the answer fields the graph's interviewer node would have
    collected, then runs the same evaluator_node the CLI uses.

    A voice answer feeds the CLEANED transcript to content scoring and keeps
    the RAW one (fillers intact) plus timing for the separate communication
    scorer — the two never share inputs.

    sandbox_result lets the caller pass in a preview run the user already
    saw, so the graded result is the one they looked at (the harness is
    LLM-generated, so re-running could differ)."""
    notes = list(run_notes or [])
    code = (code or "").strip()

    if transcript and transcript.strip():
        state["raw_transcript"] = transcript.strip()
        state["cleaned_transcript"] = clean_transcript(transcript)
        state["candidate_answer"] = state["cleaned_transcript"]
        state["answer_duration_seconds"] = duration if duration and duration > 0 else None
    else:
        state["candidate_answer"] = (answer_text or "").strip()

    if code:
        state["code_submission"] = code
        if sandbox_result is None:
            sandbox_result, more = run_submission(state["current_question"], code, language or "cpp")
            notes += more
        state["sandbox_result"] = sandbox_result

    if not state["candidate_answer"]:
        state["candidate_answer"] = (
            "(No spoken or typed explanation was given — grade the submitted code.)"
            if code
            else "(No answer was given.)"
        )

    return evaluator_node(state), notes


# ---------------------------------------------------------------------------
# Voice
# ---------------------------------------------------------------------------
def transcribe_with_cache(cache: dict, key: str, audio_bytes: bytes) -> dict:
    """Transcribe a Streamlit browser recording once and cache the result."""

    digest = hashlib.sha256(audio_bytes).hexdigest()

    hit = cache.get(key)

    if hit and hit["digest"] == digest:
        return hit

    entry = {
        "digest": digest,
        "transcript": "",
        "duration": 0.0,
        "error": None,
    }

    try:
        from tools.stt import transcribe_audio_bytes

        transcript, duration = transcribe_audio_bytes(
            audio_bytes,
            filename="answer.wav"
        )

        if not transcript.strip():
            entry["error"] = (
                "No speech was detected in that recording. "
                "Try again a little closer to the microphone."
            )
        else:
            entry["transcript"] = transcript.strip()
            entry["duration"] = duration

    except Exception as e:
        entry["error"] = f"Transcription failed: {e}"

    cache[key] = entry

    return entry


# ---------------------------------------------------------------------------
# Presentation helpers
# ---------------------------------------------------------------------------
def fmt_score(score: Optional[float]) -> str:
    return "—" if score is None else f"{score:g}/10"


def score_band(score: Optional[float]) -> str:
    if score is None:
        return "none"
    if score >= 7:
        return "good"
    if score >= 4:
        return "fair"
    return "poor"


def is_test_result(sandbox_result: Optional[dict]) -> bool:
    return bool(sandbox_result) and "tests_total" in sandbox_result


def sandbox_rows(sandbox_result: dict) -> list[dict]:
    """Per-test rows for the results table (harness-shaped results only)."""
    return [
        {
            "Test": i,
            "Expected": d["expected"],
            "Got": d["actual"] if d["actual"] is not None else "(no output)",
            "Result": "Pass" if d["passed"] else "Fail",
        }
        for i, d in enumerate(sandbox_result.get("details", []), 1)
    ]


_CF_PATTERN = re.compile(
    r'Codeforces problem: "(?P<name>.+?)" \(rated (?P<rating>\d+), tags: (?P<tags>.*?)\)\s*\n'
    r"Link: (?P<url>\S+)",
    re.S,
)


def parse_codeforces_question(text: str) -> Optional[dict]:
    """Codeforces questions are metadata + a link (the API doesn't return
    the statement), so the UI can present them as a title, tags and a
    button rather than a run-together paragraph."""
    m = _CF_PATTERN.search(text or "")
    if not m:
        return None
    tags = [t.strip() for t in m.group("tags").split(",") if t.strip()]
    return {
        "name": m.group("name"),
        "rating": int(m.group("rating")),
        "tags": tags,
        "url": m.group("url"),
    }


def round_stats(results: list[dict]) -> dict:
    contents = [r["content_score"] for r in results if r.get("content_score") is not None]
    comms = [r["communication_score"] for r in results if r.get("communication_score") is not None]

    tests_passed = tests_total = 0
    for r in results:
        sr = r.get("sandbox_result")
        if is_test_result(sr):
            tests_passed += sr["tests_passed"]
            tests_total += sr["tests_total"]

    return {
        "answered": len(results),
        "avg_content": mean(contents) if contents else None,
        "avg_communication": mean(comms) if comms else None,
        "tests_passed": tests_passed,
        "tests_total": tests_total,
    }


def round_report_md(profile: dict, rnd: dict) -> str:
    stats = round_stats(rnd["results"])
    target = " — ".join(p for p in [profile.get("company"), profile.get("role")] if p) or "No target set"

    lines = [
        "# Mock interview report",
        "",
        f"**Target:** {target}  ",
        f"**Round:** {rnd['type'].title()}  ",
        f"**Date:** {datetime.date.today().isoformat()}",
        "",
        "## Summary",
        f"- Questions answered: {stats['answered']}",
        f"- Average content score: {fmt_score(stats['avg_content'] and round(stats['avg_content'], 1))}",
    ]
    if stats["avg_communication"] is not None:
        lines.append(f"- Average communication score: {fmt_score(round(stats['avg_communication'], 1))}")
    if stats["tests_total"]:
        lines.append(f"- Test cases passed: {stats['tests_passed']}/{stats['tests_total']}")

    for i, (spec, r) in enumerate(zip(rnd["plan"], rnd["results"]), 1):
        lines += [
            "",
            f"## Q{i} — {KIND_LABELS[spec['kind']]} ({r['question_topic']} · {r['question_difficulty']})",
            "",
            "**Question**",
            "",
            *[f"> {line}" for line in r["current_question"].splitlines()],
            "",
            "**Answer**",
            "",
            r.get("raw_transcript") or r.get("candidate_answer") or "(none)",
        ]
        if r.get("code_submission"):
            lines += ["", "**Code**", "", "```", r["code_submission"], "```"]
        sr = r.get("sandbox_result")
        if is_test_result(sr):
            lines += ["", f"**Test cases:** {sr['tests_passed']}/{sr['tests_total']} passed"]
        elif sr:
            lines += ["", f"**Sandbox status:** {sr.get('status', 'unknown')}"]
        lines += ["", f"**Content:** {fmt_score(r.get('content_score'))}"]
        if r.get("communication_score") is not None:
            lines.append(f"**Communication:** {fmt_score(r['communication_score'])} — {r.get('communication_feedback', '')}")
        lines += ["", f"**Feedback:** {r.get('feedback', '')}"]

    return "\n".join(lines) + "\n"
