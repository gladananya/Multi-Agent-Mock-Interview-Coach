# # # """
# # # Shared state passed between every node in the graph.
# # # Every agent reads from and writes to this one object — this is the
# # # contract that keeps Planner / Interviewer / Evaluator decoupled.
# # # """

# # # from typing import TypedDict, Optional, List


# # # class InterviewState(TypedDict):
# # #     # --- set by Planner ---
# # #     question_topic: Optional[str]
# # #     question_difficulty: Optional[str]
# # #     topic_history: List[str]          # topics asked so far, this session

# # #     # --- set by Interviewer ---
# # #     current_question: Optional[str]
# # #     candidate_answer: Optional[str]   # will later be replaced by cleaned_transcript

# # #     # --- set by Evaluator ---
# # #     content_score: Optional[float]        # 0-10, correctness only
# # #     communication_score: Optional[float]  # 0-10, filled in once voice is added
# # #     feedback: Optional[str]

# # #     # --- reserved for later phases, unused for now ---
# # #     raw_transcript: Optional[str]
# # #     cleaned_transcript: Optional[str]
# # #     code_submission: Optional[str]
# # #     sandbox_result: Optional[dict]


# # # def initial_state() -> InterviewState:
# # #     return {
# # #         "question_topic": None,
# # #         "question_difficulty": None,
# # #         "topic_history": [],
# # #         "current_question": None,
# # #         "candidate_answer": None,
# # #         "content_score": None,
# # #         "communication_score": None,
# # #         "feedback": None,
# # #         "raw_transcript": None,
# # #         "cleaned_transcript": None,
# # #         "code_submission": None,
# # #         "sandbox_result": None,
# # #     }
# # """
# # Shared state passed between every node in the graph.
# # Every agent reads from and writes to this one object — this is the
# # contract that keeps Planner / Interviewer / Evaluator decoupled.
# # """

# # from typing import TypedDict, Optional, List


# # class InterviewState(TypedDict):
# #     # --- set by main.py at startup, from the candidate profile ---
# #     company: Optional[str]
# #     role: Optional[str]
# #     resume_text: Optional[str]

# #     # --- set by Planner ---
# #     question_topic: Optional[str]
# #     question_difficulty: Optional[str]
# #     topic_history: List[str]          # topics asked so far, this session

# #     # --- set by Interviewer ---
# #     current_question: Optional[str]
# #     candidate_answer: Optional[str]   # will later be replaced by cleaned_transcript

# #     # --- set by Evaluator ---
# #     content_score: Optional[float]        # 0-10, correctness only
# #     communication_score: Optional[float]  # 0-10, filled in once voice is added
# #     feedback: Optional[str]

# #     # --- reserved for later phases, unused for now ---
# #     raw_transcript: Optional[str]
# #     cleaned_transcript: Optional[str]
# #     code_submission: Optional[str]
# #     sandbox_result: Optional[dict]


# # def initial_state(company: str = "", role: str = "", resume_text: str = "") -> InterviewState:
# #     return {
# #         "company": company,
# #         "role": role,
# #         "resume_text": resume_text,
# #         "question_topic": None,
# #         "question_difficulty": None,
# #         "topic_history": [],
# #         "current_question": None,
# #         "candidate_answer": None,
# #         "content_score": None,
# #         "communication_score": None,
# #         "feedback": None,
# #         "raw_transcript": None,
# #         "cleaned_transcript": None,
# #         "code_submission": None,
# #         "sandbox_result": None,
# #     }
# """
# Shared state passed between every node in the graph.
# Every agent reads from and writes to this one object — this is the
# contract that keeps Planner / Interviewer / Evaluator decoupled.
# """

# from typing import TypedDict, Optional, List


# class InterviewState(TypedDict):
#     # --- set by main.py at startup, from the candidate profile ---
#     company: Optional[str]
#     role: Optional[str]
#     resume_text: Optional[str]

#     # --- set by main.py per-question, for multi-question rounds ---
#     skip_cache: bool          # True forces a fresh live fetch (used for repeated
#                               # HR questions in a Behavioral round, so they don't
#                               # all serve the same single cached entry back to back)
#     avoid_questions: List[str]  # questions already asked this round, so search/parse
#                                  # can be told not to repeat or closely resemble them

#     # --- set by Planner ---
#     question_topic: Optional[str]
#     question_difficulty: Optional[str]
#     topic_history: List[str]          # topics asked so far, this session

#     # --- set by Interviewer ---
#     current_question: Optional[str]
#     candidate_answer: Optional[str]   # will later be replaced by cleaned_transcript

#     # --- set by Evaluator ---
#     content_score: Optional[float]        # 0-10, correctness only
#     communication_score: Optional[float]  # 0-10, filled in once voice is added
#     feedback: Optional[str]

#     # --- reserved for later phases, unused for now ---
#     raw_transcript: Optional[str]
#     cleaned_transcript: Optional[str]
#     code_submission: Optional[str]
#     sandbox_result: Optional[dict]


# def initial_state(company: str = "", role: str = "", resume_text: str = "") -> InterviewState:
#     return {
#         "company": company,
#         "role": role,
#         "resume_text": resume_text,
#         "skip_cache": False,
#         "avoid_questions": [],
#         "question_topic": None,
#         "question_difficulty": None,
#         "topic_history": [],
#         "current_question": None,
#         "candidate_answer": None,
#         "content_score": None,
#         "communication_score": None,
#         "feedback": None,
#         "raw_transcript": None,
#         "cleaned_transcript": None,
#         "code_submission": None,
#         "sandbox_result": None,
#     }
"""
Shared state passed between every node in the graph.
Every agent reads from and writes to this one object — this is the
contract that keeps Planner / Interviewer / Evaluator decoupled.
"""

from typing import TypedDict, Optional, List


class InterviewState(TypedDict):
    # --- set by main.py at startup, from the candidate profile ---
    company: Optional[str]
    role: Optional[str]
    resume_text: Optional[str]

    # --- set by main.py per-question, for multi-question rounds ---
    skip_cache: bool          # True forces a fresh live fetch (used for repeated
                              # HR questions in a Behavioral round, so they don't
                              # all serve the same single cached entry back to back)
    avoid_questions: List[str]  # questions already asked this round, so search/parse
                                 # can be told not to repeat or closely resemble them

    # --- set by Planner ---
    question_topic: Optional[str]
    question_difficulty: Optional[str]
    topic_history: List[str]          # topics asked so far, this session

    # --- set by Interviewer ---
    current_question: Optional[str]
    candidate_answer: Optional[str]   # will later be replaced by cleaned_transcript

    # --- set by Evaluator ---
    content_score: Optional[float]        # 0-10, correctness only
    communication_score: Optional[float]  # 0-10, filled in once voice is added
    communication_feedback: Optional[str]
    feedback: Optional[str]

    # --- reserved for later phases, unused for now ---
    raw_transcript: Optional[str]
    cleaned_transcript: Optional[str]
    answer_duration_seconds: Optional[float]  # needed by the communication scorer
    code_submission: Optional[str]
    sandbox_result: Optional[dict]


def initial_state(company: str = "", role: str = "", resume_text: str = "") -> InterviewState:
    return {
        "company": company,
        "role": role,
        "resume_text": resume_text,
        "skip_cache": False,
        "avoid_questions": [],
        "question_topic": None,
        "question_difficulty": None,
        "topic_history": [],
        "current_question": None,
        "candidate_answer": None,
        "content_score": None,
        "communication_score": None,
        "communication_feedback": None,
        "feedback": None,
        "raw_transcript": None,
        "cleaned_transcript": None,
        "answer_duration_seconds": None,
        "code_submission": None,
        "sandbox_result": None,
    }