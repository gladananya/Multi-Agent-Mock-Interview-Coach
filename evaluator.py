# # """
# # Evaluator agent.

# # Phase 1: grades the typed answer's content only, via one LLM call.
# # Phase 5: when the candidate ran code through the sandbox, the real
# # execution result (stdout/stderr/status) is included in the prompt.
# # A soft instruction alone wasn't enough — in testing, the LLM gave a
# # 9/10 to code that had actually segfaulted. So a hard rule now runs
# # after the LLM call: if the sandbox status isn't "Accepted" (meaning
# # the code crashed, failed to compile, or timed out), the score is
# # capped deterministically in code, regardless of what the LLM decided.
# # This still isn't the same as diffing against official test cases
# # (Codeforces' API doesn't expose those) — "Accepted" here just means
# # the code ran without crashing, not that it's provably correct.
# # Phase 7 will add a second, independent scorer for communication
# # (filler words, pace) that reads raw_transcript — it must never share
# # inputs with this function, so a rambly-but-correct answer and a
# # smooth-but-wrong one don't get blended into one number.
# # """

# # import os
# # import re
# # from langchain_groq import ChatGroq
# # from state import InterviewState
# # from memory.session_store import log_attempt

# # _llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.2)

# # _CODE_FAILURE_CAP = 3.0  # max score allowed when the sandbox reports a failure

# # _PROMPT = """You are a technical interviewer grading a candidate's answer.

# # Question: {question}
# # Candidate's spoken/typed explanation: {answer}
# # {sandbox_section}
# # Score the CONTENT correctness only (ignore grammar, filler words, and delivery).
# # {sandbox_instruction}
# # Respond in exactly this format:
# # SCORE: <integer 0-10>
# # FEEDBACK: <one or two sentences, specific and constructive>
# # """

# # _SANDBOX_INSTRUCTION = (
# #     "The candidate also ran code through a sandbox — see the execution result above. "
# #     "Weigh what actually happened at runtime more heavily than the explanation: a runtime "
# #     "error, compile failure, or clearly wrong output means the code did not work, regardless "
# #     "of how confident or correct-sounding the explanation was. Note this isn't diffed against "
# #     "official test cases, so correct-looking output isn't a guarantee of a fully correct solution."
# # )


# # def _format_sandbox_section(state: InterviewState) -> str:
# #     result = state.get("sandbox_result")
# #     if not result:
# #         return ""
# #     return (
# #         f"\nCode submitted:\n{state.get('code_submission', '')}\n\n"
# #         f"Sandbox execution result:\n"
# #         f"Status: {result['status']}\n"
# #         f"Stdout: {result['stdout'] or '(empty)'}\n"
# #         f"Stderr: {result['stderr'] or '(none)'}\n"
# #         f"Compile output: {result['compile_output'] or '(none)'}\n"
# #     )


# # def _apply_sandbox_cap(state: InterviewState, score: float | None, feedback: str) -> tuple[float | None, str]:
# #     result = state.get("sandbox_result")
# #     if not result or score is None:
# #         return score, feedback

# #     if result["status"] != "Accepted" and score > _CODE_FAILURE_CAP:
# #         capped = _CODE_FAILURE_CAP
# #         feedback += (
# #             f" [Score capped at {capped:.0f}/10: the submitted code did not run successfully "
# #             f"in the sandbox (status: {result['status']}), regardless of the explanation's quality.]"
# #         )
# #         return capped, feedback

# #     return score, feedback


# # def evaluator_node(state: InterviewState) -> InterviewState:
# #     sandbox_section = _format_sandbox_section(state)
# #     prompt = _PROMPT.format(
# #         question=state["current_question"],
# #         answer=state["candidate_answer"],
# #         sandbox_section=sandbox_section,
# #         sandbox_instruction=_SANDBOX_INSTRUCTION if sandbox_section else "",
# #     )
# #     response = _llm.invoke(prompt).content

# #     score_match = re.search(r"SCORE:\s*(\d+)", response)
# #     feedback_match = re.search(r"FEEDBACK:\s*(.+)", response, re.DOTALL)

# #     score = float(score_match.group(1)) if score_match else None
# #     feedback = feedback_match.group(1).strip() if feedback_match else response.strip()

# #     score, feedback = _apply_sandbox_cap(state, score, feedback)

# #     log_attempt(state["question_topic"], state["question_difficulty"], score)

# #     state["content_score"] = score
# #     state["feedback"] = feedback
# #     return state
# """
# Evaluator agent.

# Phase 1: grades the typed answer's content only, via one LLM call.
# Phase 5: when the candidate ran code through the sandbox, the real
# execution result (stdout/stderr/status) is included in the prompt.
# A soft instruction alone wasn't enough — in testing, the LLM gave a
# 9/10 to code that had actually segfaulted. So a hard rule now runs
# after the LLM call: if the sandbox status isn't "Accepted" (meaning
# the code crashed, failed to compile, or timed out), the score is
# capped deterministically in code, regardless of what the LLM decided.
# This still isn't the same as diffing against official test cases
# (Codeforces' API doesn't expose those) — "Accepted" here just means
# the code ran without crashing, not that it's provably correct.
# Phase 7 will add a second, independent scorer for communication
# (filler words, pace) that reads raw_transcript — it must never share
# inputs with this function, so a rambly-but-correct answer and a
# smooth-but-wrong one don't get blended into one number.
# """

# import os
# import re
# from langchain_groq import ChatGroq
# from state import InterviewState
# from memory.session_store import log_attempt
# from tools.communication_scorer import score_communication

# _llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.2)

# _CODE_FAILURE_CAP = 3.0  # max score allowed when the sandbox reports a failure

# _PROMPT = """You are a technical interviewer grading a candidate's answer.

# Question: {question}
# Candidate's spoken/typed explanation: {answer}
# {sandbox_section}
# Score the CONTENT correctness only (ignore grammar, filler words, and delivery).
# {sandbox_instruction}
# Respond in exactly this format:
# SCORE: <integer 0-10>
# FEEDBACK: <one or two sentences, specific and constructive>
# """

# _SANDBOX_INSTRUCTION = (
#     "The candidate also ran code through a sandbox — see the execution result above. "
#     "Weigh what actually happened at runtime more heavily than the explanation: a runtime "
#     "error, compile failure, or clearly wrong output means the code did not work, regardless "
#     "of how confident or correct-sounding the explanation was. Note this isn't diffed against "
#     "official test cases, so correct-looking output isn't a guarantee of a fully correct solution."
# )


# def _format_sandbox_section(state: InterviewState) -> str:
#     result = state.get("sandbox_result")
#     if not result:
#         return ""
#     return (
#         f"\nCode submitted:\n{state.get('code_submission', '')}\n\n"
#         f"Sandbox execution result:\n"
#         f"Status: {result['status']}\n"
#         f"Stdout: {result['stdout'] or '(empty)'}\n"
#         f"Stderr: {result['stderr'] or '(none)'}\n"
#         f"Compile output: {result['compile_output'] or '(none)'}\n"
#     )


# def _apply_sandbox_cap(state: InterviewState, score: float | None, feedback: str) -> tuple[float | None, str]:
#     result = state.get("sandbox_result")
#     if not result or score is None:
#         return score, feedback

#     if result["status"] != "Accepted" and score > _CODE_FAILURE_CAP:
#         capped = _CODE_FAILURE_CAP
#         feedback += (
#             f" [Score capped at {capped:.0f}/10: the submitted code did not run successfully "
#             f"in the sandbox (status: {result['status']}), regardless of the explanation's quality.]"
#         )
#         return capped, feedback

#     return score, feedback


# def evaluator_node(state: InterviewState) -> InterviewState:
#     sandbox_section = _format_sandbox_section(state)
#     prompt = _PROMPT.format(
#         question=state["current_question"],
#         answer=state["candidate_answer"],
#         sandbox_section=sandbox_section,
#         sandbox_instruction=_SANDBOX_INSTRUCTION if sandbox_section else "",
#     )
#     response = _llm.invoke(prompt).content

#     score_match = re.search(r"SCORE:\s*(\d+)", response)
#     feedback_match = re.search(r"FEEDBACK:\s*(.+)", response, re.DOTALL)

#     score = float(score_match.group(1)) if score_match else None
#     feedback = feedback_match.group(1).strip() if feedback_match else response.strip()

#     score, feedback = _apply_sandbox_cap(state, score, feedback)

#     log_attempt(state["question_topic"], state["question_difficulty"], score)

#     state["content_score"] = score
#     state["feedback"] = feedback

#     # Communication scoring: independent of everything above. Uses the RAW
#     # transcript (fillers intact) + timing, computed deterministically, and
#     # never influences content_score or vice versa — see module docstring.
#     raw_transcript = state.get("raw_transcript")
#     duration = state.get("answer_duration_seconds")
#     if raw_transcript and duration:
#         comm_score, comm_feedback = score_communication(raw_transcript, duration)
#         state["communication_score"] = comm_score
#         state["communication_feedback"] = comm_feedback

#     return state
"""
Evaluator agent.

Phase 1: grades the typed answer's content only, via one LLM call.
Phase 5: when the candidate ran code through the sandbox, the real
execution result is included in the prompt. A soft instruction alone
wasn't enough — in testing, the LLM gave a 9/10 to code that had
actually segfaulted. So a hard rule runs after the LLM call:
  - Single-run sandbox_result (status/stdout/stderr/compile_output):
    if status isn't "Accepted", score is capped at _CODE_FAILURE_CAP.
  - Test-harness sandbox_result (tests_passed/tests_total): score is
    capped proportionally to the actual pass rate — 2/4 tests passing
    caps the score at 5/10, deterministically, regardless of what the
    LLM decided from the explanation alone.
Neither is the same as an official judge — Codeforces' API doesn't
expose test cases, and the harness's tests come from the question's
own worked example, not a hidden suite.
Phase 7 added a second, independent scorer for communication (filler
words, pace) that reads raw_transcript — it never shares inputs with
content scoring, so a rambly-but-correct answer isn't penalized for
correctness and a smooth-but-wrong one isn't rewarded for delivery.
"""

import os
import re
from langchain_groq import ChatGroq
from state import InterviewState
from memory.session_store import log_attempt
from tools.communication_scorer import score_communication

_llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.2)

_CODE_FAILURE_CAP = 3.0  # single-run mode: max score when the sandbox reports a failure

_PROMPT = """You are a technical interviewer grading a candidate's answer.

Question: {question}
Candidate's spoken/typed explanation: {answer}
{sandbox_section}
Score the CONTENT correctness only (ignore grammar, filler words, and delivery).
{sandbox_instruction}
Respond in exactly this format:
SCORE: <integer 0-10>
FEEDBACK: <one or two sentences, specific and constructive>
"""

_SANDBOX_INSTRUCTION = (
    "The candidate also ran code through a sandbox — see the execution result above. "
    "Weigh what actually happened at runtime more heavily than the explanation: a runtime "
    "error, compile failure, or a failed test case means the code did not fully work, "
    "regardless of how confident or correct-sounding the explanation was."
)


def _format_sandbox_section(state: InterviewState) -> str:
    result = state.get("sandbox_result")
    if not result:
        return ""

    if "tests_total" in result:
        lines = [
            f"\nCode submitted:\n{state.get('code_submission', '')}\n",
            f"Automated test-case results: {result['tests_passed']}/{result['tests_total']} passed",
        ]
        for i, d in enumerate(result.get("details", []), 1):
            verdict = "PASS" if d["passed"] else "FAIL"
            lines.append(f"  Test {i} [{verdict}]: expected={d['expected']!r} got={d['actual']!r}")
        if result.get("stderr"):
            lines.append(f"Stderr: {result['stderr']}")
        if result.get("compile_output"):
            lines.append(f"Compile output: {result['compile_output']}")
        return "\n".join(lines) + "\n"

    return (
        f"\nCode submitted:\n{state.get('code_submission', '')}\n\n"
        f"Sandbox execution result:\n"
        f"Status: {result['status']}\n"
        f"Stdout: {result['stdout'] or '(empty)'}\n"
        f"Stderr: {result['stderr'] or '(none)'}\n"
        f"Compile output: {result['compile_output'] or '(none)'}\n"
    )


def _apply_sandbox_cap(state: InterviewState, score: float | None, feedback: str) -> tuple[float | None, str]:
    result = state.get("sandbox_result")
    if not result or score is None:
        return score, feedback

    if "tests_total" in result:
        total = result["tests_total"]
        if total <= 0:
            return score, feedback
        pass_rate = result["tests_passed"] / total
        max_allowed = round(10 * pass_rate, 1)
        if score > max_allowed:
            feedback += (
                f" [Score capped at {max_allowed}/10: only {result['tests_passed']}/{total} "
                f"test cases actually passed, regardless of the explanation's quality.]"
            )
            return max_allowed, feedback
        return score, feedback

    if result["status"] != "Accepted" and score > _CODE_FAILURE_CAP:
        feedback += (
            f" [Score capped at {_CODE_FAILURE_CAP:.0f}/10: the submitted code did not run "
            f"successfully in the sandbox (status: {result['status']}), regardless of the "
            f"explanation's quality.]"
        )
        return _CODE_FAILURE_CAP, feedback

    return score, feedback


def evaluator_node(state: InterviewState) -> InterviewState:
    sandbox_section = _format_sandbox_section(state)
    prompt = _PROMPT.format(
        question=state["current_question"],
        answer=state["candidate_answer"],
        sandbox_section=sandbox_section,
        sandbox_instruction=_SANDBOX_INSTRUCTION if sandbox_section else "",
    )
    response = _llm.invoke(prompt).content

    score_match = re.search(r"SCORE:\s*(\d+)", response)
    feedback_match = re.search(r"FEEDBACK:\s*(.+)", response, re.DOTALL)

    score = float(score_match.group(1)) if score_match else None
    feedback = feedback_match.group(1).strip() if feedback_match else response.strip()

    score, feedback = _apply_sandbox_cap(state, score, feedback)

    log_attempt(state["question_topic"], state["question_difficulty"], score)

    state["content_score"] = score
    state["feedback"] = feedback

    # Communication scoring: independent of everything above. Uses the RAW
    # transcript (fillers intact) + timing, computed deterministically, and
    # never influences content_score or vice versa — see module docstring.
    raw_transcript = state.get("raw_transcript")
    duration = state.get("answer_duration_seconds")
    if raw_transcript and duration:
        comm_score, comm_feedback = score_communication(raw_transcript, duration)
        state["communication_score"] = comm_score
        state["communication_feedback"] = comm_feedback

    return state