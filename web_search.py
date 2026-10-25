# # # """
# # # For topics Codeforces can't cover (behavioral, system design), search
# # # the live web via Tavily (free tier, no card, built for LLM agents —
# # # returns clean summarized snippets rather than raw HTML) and have an
# # # LLM extract ONE clean interview question from the results.

# # # This is the most fragile part of the pipeline: search results can be
# # # noisy or off-topic, and the parser can occasionally fail to extract
# # # anything usable. Both failure modes raise, so the caller (interviewer.py)
# # # can fall back to its hardcoded bank exactly like it does for Codeforces.
# # # """

# # # import os
# # # from tavily import TavilyClient
# # # from langchain_groq import ChatGroq

# # # _client = None
# # # _parser_llm = None

# # # _PARSE_PROMPT = """Below are web search results about {difficulty} {topic} interview questions.

# # # Using these as grounding, produce exactly ONE clear, self-contained interview
# # # question suitable for a mock interview. If the results already contain a
# # # good question, use it (lightly reworded if needed for clarity). If not, write
# # # a plausible, realistic one based on the topics/themes the results discuss.

# # # Do not include any preamble, numbering, or explanation — respond with ONLY
# # # the question text itself.

# # # Only respond with NONE if the results are completely unrelated to {topic}
# # # interviews and give you nothing to ground a question in.

# # # Search results:
# # # {snippets}
# # # """


# # # def _get_client() -> TavilyClient:
# # #     global _client
# # #     if _client is None:
# # #         _client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
# # #     return _client


# # # def _get_parser_llm() -> ChatGroq:
# # #     global _parser_llm
# # #     if _parser_llm is None:
# # #         _parser_llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.3)
# # #     return _parser_llm


# # # def search_and_parse_question(topic: str, difficulty: str) -> str:
# # #     results = _get_client().search(
# # #         query=f"{difficulty} {topic} interview question",
# # #         max_results=8,
# # #     )
# # #     snippets = "\n\n".join(
# # #         f"- {r['title']}: {r['content'][:600]}"
# # #         for r in results.get("results", [])
# # #     )
# # #     if not snippets:
# # #         raise ValueError("Tavily returned no results")

# # #     prompt = _PARSE_PROMPT.format(topic=topic, difficulty=difficulty, snippets=snippets)
# # #     question = _get_parser_llm().invoke(prompt).content.strip()

# # #     if not question or question.upper() == "NONE":
# # #         raise ValueError("Parser could not extract a usable question from search results")

# # #     return question
# # """
# # For topics Codeforces can't cover (behavioral, system design), search
# # the live web via Tavily (free tier, no card, built for LLM agents —
# # returns clean summarized snippets rather than raw HTML) and have an
# # LLM extract or synthesize ONE clean interview question from the results.

# # Phase 9: company and role, when given, are folded into both the search
# # query and the framing prompt, so results (and the resulting question)
# # skew toward how that company/role actually interviews.

# # This is the most fragile part of the pipeline: search results can be
# # noisy or off-topic, and the parser can occasionally fail to extract
# # anything usable. Both failure modes raise, so the caller (interviewer.py)
# # can fall back to its hardcoded bank exactly like it does for Codeforces.
# # """

# # import os
# # from typing import Optional
# # from tavily import TavilyClient
# # from langchain_groq import ChatGroq

# # _client = None
# # _parser_llm = None

# # _PARSE_PROMPT = """Below are web search results about {difficulty} {topic} interview questions{context}.

# # Using these as grounding, produce exactly ONE clear, self-contained interview
# # question suitable for a mock interview{context}. If the results already contain
# # a good question, use it (lightly reworded if needed for clarity). If not, write
# # a plausible, realistic one based on the topics/themes the results discuss.

# # Do not include any preamble, numbering, or explanation — respond with ONLY
# # the question text itself.

# # Only respond with NONE if the results are completely unrelated to {topic}
# # interviews and give you nothing to ground a question in.

# # Search results:
# # {snippets}
# # """


# # def _get_client() -> TavilyClient:
# #     global _client
# #     if _client is None:
# #         _client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
# #     return _client


# # def _get_parser_llm() -> ChatGroq:
# #     global _parser_llm
# #     if _parser_llm is None:
# #         _parser_llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.3)
# #     return _parser_llm


# # def search_and_parse_question(
# #     topic: str,
# #     difficulty: str,
# #     company: Optional[str] = None,
# #     role: Optional[str] = None,
# # ) -> str:
# #     context_bits = [b for b in [company, role] if b]
# #     context = f" for a {' '.join(context_bits)} interview" if context_bits else ""

# #     query = f"{difficulty} {topic} interview question"
# #     if company:
# #         query += f" {company}"
# #     if role:
# #         query += f" {role}"

# #     results = _get_client().search(query=query, max_results=8)
# #     snippets = "\n\n".join(
# #         f"- {r['title']}: {r['content'][:600]}"
# #         for r in results.get("results", [])
# #     )
# #     if not snippets:
# #         raise ValueError("Tavily returned no results")

# #     prompt = _PARSE_PROMPT.format(
# #         topic=topic, difficulty=difficulty, context=context, snippets=snippets
# #     )
# #     question = _get_parser_llm().invoke(prompt).content.strip()

# #     if not question or question.upper() == "NONE":
# #         raise ValueError("Parser could not extract a usable question from search results")

# #     return question
# """
# For topics Codeforces can't cover (behavioral, system design), search
# the live web via Tavily (free tier, no card, built for LLM agents —
# returns clean summarized snippets rather than raw HTML) and have an
# LLM extract or synthesize ONE clean interview question from the results.

# Phase 9: company and role, when given, are folded into both the search
# query and the framing prompt, so results (and the resulting question)
# skew toward how that company/role actually interviews.

# This is the most fragile part of the pipeline: search results can be
# noisy or off-topic, and the parser can occasionally fail to extract
# anything usable. Both failure modes raise, so the caller (interviewer.py)
# can fall back to its hardcoded bank exactly like it does for Codeforces.
# """

# import os
# from typing import Optional
# from tavily import TavilyClient
# from langchain_groq import ChatGroq

# _client = None
# _parser_llm = None

# _PARSE_PROMPT = """Below are web search results about {difficulty} {topic} interview questions{context}.

# Using these as grounding, produce exactly ONE clear, self-contained interview
# question suitable for a mock interview{context}. If the results already contain
# a good question, use it (lightly reworded if needed for clarity). If not, write
# a plausible, realistic one based on the topics/themes the results discuss.

# If this is a coding/algorithmic question, include a brief example input and
# expected output so it's actually attemptable in code.

# Do not include any preamble, numbering, or explanation — respond with ONLY
# the question text itself.

# Only respond with NONE if the results are completely unrelated to {topic}
# interviews and give you nothing to ground a question in.

# Search results:
# {snippets}
# """


# def _get_client() -> TavilyClient:
#     global _client
#     if _client is None:
#         _client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
#     return _client


# def _get_parser_llm() -> ChatGroq:
#     global _parser_llm
#     if _parser_llm is None:
#         _parser_llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.3)
#     return _parser_llm


# def search_and_parse_question(
#     topic: str,
#     difficulty: str,
#     company: Optional[str] = None,
#     role: Optional[str] = None,
# ) -> str:
#     context_bits = [b for b in [company, role] if b]
#     context = f" for a {' '.join(context_bits)} interview" if context_bits else ""

#     query = f"{difficulty} {topic} interview question"
#     if company:
#         query += f" {company}"
#     if role:
#         query += f" {role}"

#     results = _get_client().search(query=query, max_results=8)
#     snippets = "\n\n".join(
#         f"- {r['title']}: {r['content'][:600]}"
#         for r in results.get("results", [])
#     )
#     if not snippets:
#         raise ValueError("Tavily returned no results")

#     prompt = _PARSE_PROMPT.format(
#         topic=topic, difficulty=difficulty, context=context, snippets=snippets
#     )
#     question = _get_parser_llm().invoke(prompt).content.strip()

#     if not question or question.upper() == "NONE":
#         raise ValueError("Parser could not extract a usable question from search results")

#     return question
"""
For topics Codeforces can't cover (behavioral, system design), search
the live web via Tavily (free tier, no card, built for LLM agents —
returns clean summarized snippets rather than raw HTML) and have an
LLM extract or synthesize ONE clean interview question from the results.

Phase 9: company and role, when given, are folded into both the search
query and the framing prompt, so results (and the resulting question)
skew toward how that company/role actually interviews.

This is the most fragile part of the pipeline: search results can be
noisy or off-topic, and the parser can occasionally fail to extract
anything usable. Both failure modes raise, so the caller (interviewer.py)
can fall back to its hardcoded bank exactly like it does for Codeforces.
"""

import os
from typing import Optional
from tavily import TavilyClient
from langchain_groq import ChatGroq

_client = None
_parser_llm = None

_PARSE_PROMPT = """Below are web search results about {difficulty} {topic} interview questions{context}.

Using these as grounding, produce exactly ONE clear, self-contained interview
question suitable for a mock interview{context}. If the results already contain
a good question, use it (lightly reworded if needed for clarity). If not, write
a plausible, realistic one based on the topics/themes the results discuss.

If this is a coding/algorithmic question, include a brief example input and
expected output so it's actually attemptable in code.
{avoid_section}
Do not include any preamble, numbering, or explanation — respond with ONLY
the question text itself.

Only respond with NONE if the results are completely unrelated to {topic}
interviews and give you nothing to ground a question in.

Search results:
{snippets}
"""


def _get_client() -> TavilyClient:
    global _client
    if _client is None:
        _client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    return _client


def _get_parser_llm() -> ChatGroq:
    global _parser_llm
    if _parser_llm is None:
        _parser_llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.3)
    return _parser_llm


def search_and_parse_question(
    topic: str,
    difficulty: str,
    company: Optional[str] = None,
    role: Optional[str] = None,
    avoid: Optional[list[str]] = None,
) -> str:
    context_bits = [b for b in [company, role] if b]
    context = f" for a {' '.join(context_bits)} interview" if context_bits else ""

    query = f"{difficulty} {topic} interview question"
    if company:
        query += f" {company}"
    if role:
        query += f" {role}"

    results = _get_client().search(query=query, max_results=8)
    snippets = "\n\n".join(
        f"- {r['title']}: {r['content'][:600]}"
        for r in results.get("results", [])
    )
    if not snippets:
        raise ValueError("Tavily returned no results")

    avoid_section = ""
    if avoid:
        listed = "\n".join(f"- {q}" for q in avoid)
        avoid_section = (
            f"\nDo NOT repeat or closely resemble any of these already-asked "
            f"questions:\n{listed}\n"
        )

    prompt = _PARSE_PROMPT.format(
        topic=topic, difficulty=difficulty, context=context,
        avoid_section=avoid_section, snippets=snippets,
    )
    question = _get_parser_llm().invoke(prompt).content.strip()

    if not question or question.upper() == "NONE":
        raise ValueError("Parser could not extract a usable question from search results")

    return question