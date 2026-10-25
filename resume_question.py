"""
When the candidate has provided a resume, behavioral questions can be
grounded in their actual projects/experience instead of being generic.
Uses the LLM directly (no search needed — this is about the candidate's
own resume, not general web content), so it's not cached: a resume can
change, and the question is specific to this one candidate anyway.
"""

from typing import Optional
from langchain_groq import ChatGroq

_llm = None

_PROMPT = """You are a technical interviewer for a {role} position at {company}.

Below is the candidate's resume. Ask exactly ONE specific, realistic
interview question that references a real project, skill, or experience
from their resume — the way a real interviewer who actually read the
resume would. Prefer questions that probe a technical decision, a
challenge faced, or a trade-off made, over generic "tell me about X".
{avoid_section}
Do not include any preamble or explanation — respond with ONLY the
question text itself.

Resume:
{resume_text}
"""


def _get_llm() -> ChatGroq:
    global _llm
    if _llm is None:
        _llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.4)
    return _llm


def generate_resume_question(
    resume_text: str,
    role: Optional[str],
    company: Optional[str],
    avoid: Optional[list[str]] = None,
) -> str:
    if not resume_text or not resume_text.strip():
        raise ValueError("No resume text available")

    avoid_section = ""
    if avoid:
        listed = "\n".join(f"- {q}" for q in avoid)
        avoid_section = (
            f"\nDo NOT ask a question that repeats or closely resembles any of "
            f"these already-asked questions — pick a different project, skill, "
            f"or decision from the resume instead:\n{listed}\n"
        )

    prompt = _PROMPT.format(
        role=role or "Software Engineer",
        company=company or "a tech company",
        avoid_section=avoid_section,
        resume_text=resume_text,
    )
    question = _get_llm().invoke(prompt).content.strip()

    if not question:
        raise ValueError("LLM returned an empty question")

    return question