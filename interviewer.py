"""
Interviewer agent.

Phase 10: DSA question sourcing now mirrors the behavioral flow.
Codeforces has no public company-tagging, so when a target company is
set, a company/role-aware live search (tools/web_search.py) is tried
FIRST — grounded in real reported interview questions (GeeksforGeeks/
LeetCode-discuss-style content), not LLM-hallucinated ones, so it's
safer than pure generation while still being company-relevant.
Codeforces is the fallback: no company match, but a guaranteed real,
solvable problem. Tiers, in order, for DSA topics:
  1. Company/role-aware live search — only tried if a company is set.
     Cached per (topic, difficulty, company, role).
  2. Codeforces — generic but a real, verified problem.
     Cached per (topic, difficulty), company/role left blank.
  3. Hardcoded fallback bank.

Behavioral topics unchanged from Phase 9 (resume-grounded first, then
company/role-aware search, then fallback bank).

Phase 7 will swap input() for tools/stt.py — everything downstream
(state["candidate_answer"]) stays the same shape either way.
"""

from state import InterviewState
from tools.codeforces_api import get_problem
from tools.web_search import search_and_parse_question
from tools.resume_question import generate_resume_question
from tools.sandbox import run_code
from memory.question_cache import get_cached_question, store_question

DSA_TOPICS = {"arrays", "graphs", "dynamic programming"}
_DSA_TOPICS = DSA_TOPICS  # kept for internal readability, same object

_FALLBACK_BANK = {
    "arrays": "Given an array of integers, find two numbers that add up to a target sum. Walk me through your approach.",
    "graphs": "How would you detect a cycle in a directed graph? Explain your approach and its time complexity.",
    "dynamic programming": "Explain how you'd solve the 0/1 knapsack problem, and why a greedy approach doesn't work here.",
    "behavioral": "Tell me about a time you disagreed with a teammate's technical decision. How did you handle it?",
}


def _fetch_from_codeforces(topic: str, difficulty: str) -> str:
    problem = get_problem(topic, difficulty)
    tags = ", ".join(problem["tags"])
    return (
        f'Codeforces problem: "{problem["name"]}" (rated {problem["rating"]}, tags: {tags})\n'
        f"Link: {problem['url']}\n"
        f"Open the link, read the problem, then explain your approach out loud."
    )


def _build_dsa_question(state: InterviewState) -> str:
    topic = state["question_topic"]
    difficulty = state["question_difficulty"]
    company = state.get("company")
    role = state.get("role")
    skip_cache = state.get("skip_cache", False)
    avoid = state.get("avoid_questions") or []

    # Tier 1: company-flavored live search, only if a company is actually set
    if company:
        if not skip_cache:
            cached = get_cached_question(topic, difficulty, company=company, role=role)
            if cached is not None:
                print("[Served from cache]")
                return cached
        try:
            question = search_and_parse_question(
                topic, difficulty, company=company, role=role, avoid=avoid
            )
            store_question(topic, difficulty, question, source="web_search", company=company, role=role)
            return question
        except Exception as e:
            print(f"[Company-specific search failed ({e}), trying Codeforces]")

    # Tier 2: Codeforces, generic but a real, verified problem. Random.choice
    # among matching problems already gives variety on a fresh fetch, so
    # skip_cache alone (no text-level avoid needed) is enough here.
    if not skip_cache:
        cached = get_cached_question(topic, difficulty)
        if cached is not None:
            print("[Served from cache]")
            return cached
    try:
        question = _fetch_from_codeforces(topic, difficulty)
        store_question(topic, difficulty, question, source="codeforces")
        return question
    except Exception as e:
        print(f"[Codeforces lookup failed ({e}), using fallback question]")
        return _FALLBACK_BANK[topic]


def _build_behavioral_question(state: InterviewState) -> str:
    topic = state["question_topic"]
    difficulty = state["question_difficulty"]
    company = state.get("company")
    role = state.get("role")
    resume_text = state.get("resume_text")

    # Tier 1: resume-grounded (not cached, per-candidate)
    if resume_text:
        try:
            avoid = state.get("avoid_questions") or []
            question = generate_resume_question(resume_text, role, company, avoid=avoid)
            print("[Resume-grounded question]")
            return question
        except Exception as e:
            print(f"[Resume-grounded generation failed ({e}), trying live search]")

    # Tier 2: company/role-aware live search, cached — unless skip_cache is set
    # (used for repeated HR questions in a Behavioral round, so they don't all
    # serve the same single cached entry back to back)
    skip_cache = state.get("skip_cache", False)
    avoid = state.get("avoid_questions") or []

    if not skip_cache:
        cached = get_cached_question(topic, difficulty, company=company, role=role)
        if cached is not None:
            print("[Served from cache]")
            return cached
    try:
        question = search_and_parse_question(
            topic, difficulty, company=company, role=role, avoid=avoid
        )
        store_question(topic, difficulty, question, source="web_search", company=company, role=role)
        return question
    except Exception as e:
        print(f"[Live lookup failed ({e}), using fallback question]")
        return _FALLBACK_BANK.get(topic, "Tell me about a challenging bug you fixed recently.")


def _build_question(state: InterviewState) -> str:
    if state["question_topic"] in _DSA_TOPICS:
        return _build_dsa_question(state)
    return _build_behavioral_question(state)


def fetch_question(state: InterviewState) -> InterviewState:
    """Non-interactive counterpart to interviewer_node: sources the question
    and stops. The web UI (app.py) collects the answer with widgets instead
    of the blocking input() calls interviewer_node makes, so it needs the
    question-sourcing half on its own."""
    state["current_question"] = _build_question(state)
    return state


def fetch_question(state: InterviewState) -> InterviewState:
    """Non-blocking counterpart to interviewer_node, for the web UI.
    interviewer_node also calls _collect_answer (which uses input()) and
    _maybe_run_code — both block on a terminal prompt, which a browser UI
    has no way to satisfy. This does only the part that's safe to call from
    Streamlit: pick the question and stash it in state, and return
    immediately so app.py can render it and collect the answer through its
    own widgets instead."""
    topic = state["question_topic"]
    question = _build_question(state)
    state["current_question"] = question
    return state


def _read_multiline_answer(prompt: str) -> str:
    print(f"\n{prompt} (type a line with just ### when you're done):")
    lines = []
    while True:
        line = input()
        if line.strip() == "###":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def _collect_answer(state: InterviewState) -> None:
    """Offers voice or typed input. Mutates state in place. On any voice
    failure (no mic, PortAudio missing, transcription error), falls back
    to typed input rather than crashing — same pattern as every other
    external dependency in this project."""
    mode = input("\nAnswer via (1) typed text or (2) voice? [1/2, default 1]: ").strip()

    if mode == "2":
        try:
            from tools.stt import record_and_transcribe
            from tools.transcript_cleaner import clean_transcript

            raw_transcript, duration = record_and_transcribe()
            print(f"\n[Transcribed]: {raw_transcript}")

            state["raw_transcript"] = raw_transcript
            state["cleaned_transcript"] = clean_transcript(raw_transcript)
            state["candidate_answer"] = state["cleaned_transcript"]
            state["answer_duration_seconds"] = duration
            return
        except Exception as e:
            print(f"[Voice input failed ({e}), switching to typed answer]")

    state["candidate_answer"] = _read_multiline_answer("Your answer")


def _maybe_run_code(state: InterviewState) -> None:
    """For DSA topics, optionally collect and execute code. Mutates state in place.

    Tries the auto-generated test-case harness first (tools/test_harness.py):
    the candidate pastes just their Solution class/function, and the worked
    example already in the question is used to build the driver code and
    grade pass/fail per test case. This only works when the question actually
    contains a worked example — true for company-search-sourced questions,
    not for Codeforces-linked ones (metadata only) or the fallback bank — so
    on any failure it cleanly falls back to the old single-run flow, where
    the candidate provides their own complete runnable program.
    """
    choice = input("\nWant to also run your code through the sandbox? (y/n): ").strip().lower()
    if choice != "y":
        return

    language = input("Language (python/cpp/java/javascript): ").strip().lower()
    print(
        "Paste just your Solution class/function if the question has a worked "
        "example — a test harness will be built for you automatically. If "
        "that's not possible for this question, you'll need a complete "
        "runnable program instead (a main() that calls your solution and "
        "prints the result). Standard C++ headers are added for you either way."
    )
    code = _read_multiline_answer("Paste your code")
    state["code_submission"] = code

    try:
        from tools.test_harness import run_test_cases
        test_result = run_test_cases(state["current_question"], code, language)
        state["sandbox_result"] = test_result

        print(f"\n[Test cases: {test_result['tests_passed']}/{test_result['tests_total']} passed]")
        for i, d in enumerate(test_result["details"], 1):
            mark = "PASS" if d["passed"] else "FAIL"
            print(f"  [{mark}] Test {i}: expected={d['expected']!r} got={d['actual']!r}")
        if test_result["stderr"]:
            print(f"stderr: {test_result['stderr']}")
        if test_result["compile_output"]:
            print(f"compile output: {test_result['compile_output']}")
        return
    except Exception as e:
        print(f"[Automated test-case grading unavailable ({e}) — falling back to a single run]")

    try:
        result = run_code(code, language)
        state["sandbox_result"] = result
        print(f"\n[Sandbox status: {result['status']}]")
        if result["stdout"]:
            print(f"stdout: {result['stdout']}")
        if result["stderr"]:
            print(f"stderr: {result['stderr']}")
        if result["compile_output"]:
            print(f"compile output: {result['compile_output']}")
    except Exception as e:
        print(f"[Sandbox execution failed: {e}]")
        state["sandbox_result"] = None


def interviewer_node(state: InterviewState) -> InterviewState:
    topic = state["question_topic"]
    difficulty = state["question_difficulty"]
    question = _build_question(state)
    state["current_question"] = question

    print(f"\n[{difficulty.upper()} | {topic}]")
    print(question)
    _collect_answer(state)

    if topic in _DSA_TOPICS:
        _maybe_run_code(state)

    return state
