"""
Streamlit UI for the interview agent.   Run:  streamlit run app.py

Stages:  setup -> question -> feedback -> (next question ...) -> summary

Everything that isn't a widget lives in ui_logic.py (no Streamlit import
there, so it's unit-testable). This file only draws the interface and
moves between stages.

Two Streamlit behaviours this file is written around:
  * The whole script reruns on every interaction, so anything expensive
    (fetching a question, transcribing audio, running code) is done once
    and kept in st.session_state, never recomputed on a rerun.
  * A widget's state is dropped on any run where the widget isn't drawn,
    which would wipe typed text when you flip between Typing and Speaking.
    The "keep" loop at the top of _stage_question re-assigns those values
    so they survive.
"""

import html
import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Interview Agent", page_icon="🎯", layout="wide")

if not os.environ.get("GROQ_API_KEY"):
    st.title("Interview Agent")
    st.error("GROQ_API_KEY isn't set. Copy `.env.example` to `.env`, add your key, and restart the app.")
    st.stop()

# These imports must come after the key check: evaluator.py builds its Groq
# client at import time and would raise without a key.
import ui_logic  # noqa: E402
from memory.candidate_profile import get_profile, set_profile  # noqa: E402
from memory.session_store import get_topic_performance, get_attempt_history  # noqa: E402
from tools.resume_reader import extract_text_from_pdf  # noqa: E402

st.markdown(
    """
    <style>
    .block-container { padding-top: 2.2rem; max-width: 1250px; }
    .pill { display:inline-block; padding:2px 10px; margin:0 6px 8px 0; border-radius:999px;
            font-size:0.78rem; font-weight:600; background:#E3F4F0; color:#0F766E;
            border:1px solid #B5DDD6; }
    .pill-muted { background:#F1F3F5; color:#495057; border-color:#DEE2E6; }
    textarea[aria-label="Your code"] { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace !important;
                                       font-size: 0.85rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

_DEFAULTS = {
    "stage": "setup",
    "profile": None,       # {"company", "role", "resume_text"} once a round has started
    "round": None,         # the dict from ui_logic.new_round()
    "current": None,       # InterviewState for the question on screen
    "question_notes": [],  # where the current question came from
    "result": None,        # graded state, shown on the feedback stage
    "grade_notes": [],
    "voice": {},           # transcription cache, see ui_logic.transcribe_with_cache
    "runs": {},            # preview sandbox runs, keyed by question
}
for _key, _value in _DEFAULTS.items():
    st.session_state.setdefault(_key, _value)


def _reset_round() -> None:
    for key in ("round", "current", "result"):
        st.session_state[key] = None
    st.session_state.question_notes = []
    st.session_state.grade_notes = []
    st.session_state.voice = {}
    st.session_state.runs = {}


def _pills(items: list[tuple[str, bool]]) -> None:
    body = "".join(
        f'<span class="pill{" pill-muted" if muted else ""}">{html.escape(text)}</span>'
        for text, muted in items
    )
    st.markdown(body, unsafe_allow_html=True)


def _render_sandbox(result: dict | None) -> None:
    if result is None:
        st.warning("The sandbox couldn't run your code.")
        return

    if ui_logic.is_test_result(result):
        passed, total = result["tests_passed"], result["tests_total"]
        (st.success if total and passed == total else st.warning)(f"{passed} of {total} test cases passed")
        rows = ui_logic.sandbox_rows(result)
        if rows:
            st.dataframe(pd.DataFrame(rows), hide_index=True)
        if result.get("status") and result["status"] != "Accepted":
            st.caption(f"Sandbox status: {result['status']}")
    else:
        st.markdown(f"**Sandbox status:** {result['status']}")
        if result.get("stdout"):
            st.caption("Output")
            st.code(result["stdout"], language="text")

    if result.get("compile_output"):
        st.caption("Compiler output")
        st.code(result["compile_output"], language="text")
    if result.get("stderr"):
        st.caption("Errors")
        st.code(result["stderr"], language="text")


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
def _sidebar() -> None:
    with st.sidebar:
        st.markdown("### Interview Agent")

        profile = st.session_state.profile
        if profile:
            st.caption(" · ".join(p for p in [profile["company"], profile["role"]] if p) or "No target set")

        rnd = st.session_state.round
        if rnd and st.session_state.stage in ("question", "feedback"):
            done, total = len(rnd["results"]), len(rnd["plan"])
            st.progress(done / total, text=f"{done} of {total} answered")
            if st.button("End round", key="end_round"):
                st.session_state.stage = "summary" if rnd["results"] else "setup"
                if not rnd["results"]:
                    _reset_round()
                st.session_state.current = None
                st.rerun()

        st.markdown("#### Your topics")
        perf = get_topic_performance()
        if perf:
            df = pd.DataFrame(
                [
                    {"Topic": t.title(), "Avg": v["avg_score"], "Tries": v["attempts"], "Level": v["last_difficulty"]}
                    for t, v in sorted(perf.items())
                ]
            )
            st.dataframe(
                df,
                hide_index=True,
                column_config={"Avg": st.column_config.ProgressColumn("Avg /10", min_value=0, max_value=10, format="%.1f")},
            )
            st.caption("The planner picks your weakest topic next.")
        else:
            st.caption("No scored answers yet. Your topic averages will appear here.")

        if not os.environ.get("TAVILY_API_KEY"):
            st.warning("TAVILY_API_KEY isn't set, so live web search is off. Questions fall back to Codeforces and the built-in bank.")


# ---------------------------------------------------------------------------
# Stage: setup
# ---------------------------------------------------------------------------
def _stage_setup() -> None:
    st.title("Mock interview")
    st.caption("Set a target, pick a round, then answer by typing or speaking. Code is run against test cases.")

    saved = get_profile() or {}
    saved_resume = saved.get("resume_text", "")
    left, right = st.columns([3, 2], gap="large")

    with left:
        with st.container(border=True):
            st.subheader("Your target")
            c1, c2 = st.columns(2)
            company = c1.text_input("Company", value=saved.get("company", ""), key="company", placeholder="e.g. Google")
            role = c2.text_input("Role", value=saved.get("role", ""), key="role", placeholder="e.g. SDE Intern")

            st.markdown("**Resume**")
            if saved_resume:
                st.caption(f"A saved resume is on file ({len(saved_resume):,} characters). Add one below only to replace it.")
            tab_pdf, tab_text = st.tabs(["Upload PDF", "Paste text"])
            with tab_pdf:
                pdf = st.file_uploader("Resume PDF", type=["pdf"], key="resume_pdf", label_visibility="collapsed")
            with tab_text:
                pasted = st.text_area(
                    "Resume text", height=170, key="resume_paste",
                    placeholder="Paste your resume text here", label_visibility="collapsed",
                )

            # precedence: an uploaded PDF, then pasted text, then what's saved
            resume_text = saved_resume
            if pdf is not None:
                try:
                    resume_text = extract_text_from_pdf(pdf.getvalue())
                    st.success(f"Read {len(resume_text):,} characters from {pdf.name}")
                except ValueError as e:
                    st.error(str(e))
            elif pasted.strip():
                resume_text = pasted.strip()

    with right:
        with st.container(border=True):
            st.subheader("Round")
            choice = st.radio(
                "Round type",
                ["Technical", "Behavioral"],
                key="round_choice",
                captions=["1 DSA question + 1 question about your resume", "HR-style questions, one after another"],
            )
            hr_count = 3
            if choice == "Behavioral":
                hr_count = st.slider("Number of questions", 1, 8, 3, key="hr_count")
            elif not resume_text.strip():
                st.warning("No resume yet, so the resume question will fall back to a general HR-style one.")

            if st.button("Start round", type="primary", key="start_round"):
                profile = {"company": company.strip(), "role": role.strip(), "resume_text": resume_text}
                set_profile(profile["company"], profile["role"], profile["resume_text"])
                _reset_round()
                st.session_state.profile = profile
                st.session_state.round = ui_logic.new_round(
                    ui_logic.TECHNICAL if choice == "Technical" else ui_logic.BEHAVIORAL, hr_count
                )
                st.session_state.stage = "question"
                st.rerun()


# ---------------------------------------------------------------------------
# Stage: question
# ---------------------------------------------------------------------------
def _answer_panel(state: dict, k: str, is_dsa: bool) -> dict:
    st.markdown("#### Your answer")
    mode = st.radio("Answer by", ["Typing", "Speaking"], horizontal=True, key=f"mode_{k}", label_visibility="collapsed")

    text, transcript, duration = "", None, None
    if mode == "Typing":
        text = st.text_area(
            "Answer", height=180, key=f"text_{k}",
            placeholder="Explain your approach…", label_visibility="collapsed",
        )
    else:
        audio = st.audio_input("Record your answer", key=f"audio_{k}")
        if audio is not None:
            with st.spinner("Transcribing…"):
                entry = ui_logic.transcribe_with_cache(st.session_state.voice, k, audio.getvalue())
            if entry["error"]:
                st.error(entry["error"])
            else:
                transcript, duration = entry["transcript"], entry["duration"]
                st.info(f"**What we heard:** {transcript}")
                if not duration:
                    st.caption("Couldn't read the recording length, so there won't be a communication score.")

    code, language = "", None
    if is_dsa:
        st.markdown("#### Code (optional)")
        language = st.selectbox("Language", ui_logic.LANGUAGES, key=f"lang_{k}")
        code = st.text_area("Your code", height=280, key=f"code_{k}", label_visibility="collapsed",
                            placeholder="Paste your solution here")
        st.caption(
            "If the question has a worked example, paste just your Solution class. A test harness is built "
            "for you and run against it. Otherwise, include a complete program with a main(). "
            "Standard C++ headers are added automatically."
        )

        if st.button("Run code", key=f"run_{k}"):
            if not code.strip():
                st.warning("Paste some code first.")
            else:
                with st.spinner("Running in the sandbox…"):
                    result, notes = ui_logic.run_submission(state["current_question"], code, language)
                st.session_state.runs[k] = {"sig": ui_logic.code_signature(code, language), "result": result, "notes": notes}

        run = st.session_state.runs.get(k)
        if run:
            if code.strip() and run["sig"] != ui_logic.code_signature(code, language):
                st.caption("You've edited the code since this run. It will be run again when you submit.")
            for note in run["notes"]:
                st.info(note)
            _render_sandbox(run["result"])

    st.divider()
    submitted = st.button("Submit answer", type="primary", key=f"submit_{k}")
    return {"text": text, "transcript": transcript, "duration": duration,
            "code": code, "language": language, "submitted": submitted}


def _submit(state: dict, k: str, answer: dict) -> None:
    reuse, notes = None, []
    run = st.session_state.runs.get(k)
    if answer["code"].strip() and run and run["sig"] == ui_logic.code_signature(answer["code"], answer["language"]):
        reuse, notes = run["result"], run["notes"]

    with st.spinner("Scoring your answer…"):
        try:
            graded, grade_notes = ui_logic.grade(
                state,
                answer_text=answer["text"],
                transcript=answer["transcript"],
                duration=answer["duration"],
                code=answer["code"],
                language=answer["language"],
                sandbox_result=reuse,
                run_notes=notes,
            )
        except Exception as e:
            st.error(f"Scoring failed: {e}. Your answer is still here, so you can submit again.")
            return

    st.session_state.result = graded
    st.session_state.grade_notes = grade_notes
    st.session_state.stage = "feedback"
    st.rerun()


def _stage_question() -> None:
    rnd = st.session_state.round
    idx, total = rnd["index"], len(rnd["plan"])
    spec = rnd["plan"][idx]
    k = f"{rnd['id']}_{idx}"

    if st.session_state.current is None:
        with st.spinner("Finding a question. This can take a few seconds…"):
            try:
                state, notes = ui_logic.load_question(rnd, st.session_state.profile)
            except Exception as e:
                st.error(f"Couldn't load a question: {e}")
                st.button("Try again", key=f"retry_{k}")
                return
        st.session_state.current = state
        st.session_state.question_notes = notes

    # widget state is dropped on runs where the widget isn't drawn (e.g. while
    # on the Speaking tab); re-assigning keeps typed text and code alive
    for key in (f"text_{k}", f"code_{k}", f"lang_{k}", f"mode_{k}"):
        if key in st.session_state:
            st.session_state[key] = st.session_state[key]

    state = st.session_state.current
    is_dsa = state["question_topic"] in ui_logic.DSA_TOPICS
    question = state["current_question"]

    st.progress(idx / total, text=f"Question {idx + 1} of {total}")
    left, right = st.columns(2, gap="large")

    with left:
        _pills([
            (ui_logic.KIND_LABELS[spec["kind"]], False),
            (state["question_difficulty"].title(), True),
            (state["question_topic"].title(), True),
        ])
        with st.container(border=True):
            cf = ui_logic.parse_codeforces_question(question)
            if cf:
                st.markdown(f"#### {cf['name']}")
                _pills([(f"Rated {cf['rating']}", True)] + [(t, True) for t in cf["tags"]])
                st.link_button("Open the problem on Codeforces", cf["url"])
                st.caption("Read the problem there, then explain your approach here. You can also run code.")
            else:
                st.markdown(question)
        if st.session_state.question_notes:
            st.caption("Source: " + " · ".join(n.strip("[]") for n in st.session_state.question_notes))

    with right:
        answer = _answer_panel(state, k, is_dsa)

    if answer["submitted"]:
        if not (answer["text"].strip() or answer["transcript"] or answer["code"].strip()):
            st.warning("Add an answer, a recording, or some code before submitting.")
        else:
            _submit(state, k, answer)


# ---------------------------------------------------------------------------
# Stage: feedback
# ---------------------------------------------------------------------------
def _stage_feedback() -> None:
    rnd, state = st.session_state.round, st.session_state.result
    idx, total = rnd["index"], len(rnd["plan"])

    st.progress((idx + 1) / total, text=f"Question {idx + 1} of {total}, scored")
    st.subheader("Your result")

    c1, c2, c3 = st.columns(3)
    c1.metric("Content", ui_logic.fmt_score(state.get("content_score")), border=True,
              help="How correct and complete your answer was.")
    comm = state.get("communication_score")
    c2.metric("Communication", ui_logic.fmt_score(comm), border=True,
              help="Filler words and pace, scored separately from correctness. Spoken answers only.")
    sr = state.get("sandbox_result")
    if ui_logic.is_test_result(sr):
        c3.metric("Test cases", f"{sr['tests_passed']}/{sr['tests_total']}", border=True)
    elif sr:
        c3.metric("Sandbox", sr["status"], border=True)
    else:
        c3.metric("Code", "Not run", border=True)
    if comm is not None:
        c2.caption(state.get("communication_feedback", ""))

    if state.get("content_score") is None:
        st.warning("The scorer didn't return a readable score for this answer.")
    with st.container(border=True):
        st.markdown("**Feedback**")
        st.write(state.get("feedback") or "No feedback was returned.")

    for note in st.session_state.grade_notes:
        st.info(note)

    if state.get("raw_transcript"):
        with st.expander("What we heard"):
            st.write(state["raw_transcript"])
    elif state.get("candidate_answer"):
        with st.expander("Your answer"):
            st.write(state["candidate_answer"])
    if state.get("code_submission"):
        with st.expander("Your code and test results", expanded=True):
            st.code(state["code_submission"], language="cpp")
            _render_sandbox(sr)
    with st.expander("The question"):
        st.markdown(state["current_question"])

    is_last = idx + 1 >= total
    if st.button("Finish round" if is_last else "Next question", type="primary", key=f"next_{rnd['id']}_{idx}"):
        done = ui_logic.finish_question(rnd, state)
        st.session_state.current = None
        st.session_state.result = None
        st.session_state.question_notes = []
        st.session_state.grade_notes = []
        st.session_state.stage = "summary" if done else "question"
        st.rerun()


# ---------------------------------------------------------------------------
# Stage: summary
# ---------------------------------------------------------------------------
def _stage_summary() -> None:
    rnd, profile = st.session_state.round, st.session_state.profile
    results = rnd["results"]
    stats = ui_logic.round_stats(results)

    st.title("Round complete")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Answered", stats["answered"], border=True)
    avg = stats["avg_content"]
    c2.metric("Avg content", ui_logic.fmt_score(None if avg is None else round(avg, 1)), border=True)
    avg_c = stats["avg_communication"]
    c3.metric("Avg communication", ui_logic.fmt_score(None if avg_c is None else round(avg_c, 1)), border=True)
    c4.metric("Test cases", f"{stats['tests_passed']}/{stats['tests_total']}" if stats["tests_total"] else "—", border=True)

    st.subheader("Question by question")
    for i, (spec, r) in enumerate(zip(rnd["plan"], results), 1):
        title = f"Q{i} · {ui_logic.KIND_LABELS[spec['kind']]} · {ui_logic.fmt_score(r.get('content_score'))}"
        with st.expander(title, expanded=len(results) == 1):
            st.markdown(r["current_question"])
            st.markdown("**Feedback**")
            st.write(r.get("feedback") or "—")
            if r.get("communication_score") is not None:
                st.caption(f"Communication {ui_logic.fmt_score(r['communication_score'])}: {r.get('communication_feedback', '')}")
            if ui_logic.is_test_result(r.get("sandbox_result")):
                sr = r["sandbox_result"]
                st.caption(f"Test cases: {sr['tests_passed']}/{sr['tests_total']} passed")

    st.subheader("Your progress")
    history = get_attempt_history()
    if len(history) >= 2:
        df = pd.DataFrame(history)
        df["Attempt"] = range(1, len(df) + 1)
        p1, p2 = st.columns(2, gap="large")
        with p1:
            st.caption("Score on every scored answer")
            st.line_chart(df, x="Attempt", y="score")
        with p2:
            st.caption("Average score by topic")
            perf = get_topic_performance()
            st.bar_chart(pd.DataFrame({"Avg": {t.title(): v["avg_score"] for t, v in perf.items()}}))
    else:
        st.caption("Answer a few more questions and your trend will show up here.")

    b1, b2, _ = st.columns([1, 1, 3])
    if b1.button("Start another round", type="primary", key="another_round"):
        _reset_round()
        st.session_state.stage = "setup"
        st.rerun()
    b2.download_button(
        "Download report", data=ui_logic.round_report_md(profile, rnd),
        file_name="mock-interview-report.md", mime="text/markdown", key="download_report",
    )


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
_sidebar()
{
    "setup": _stage_setup,
    "question": _stage_question,
    "feedback": _stage_feedback,
    "summary": _stage_summary,
}[st.session_state.stage]()
