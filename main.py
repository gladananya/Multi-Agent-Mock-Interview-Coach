# # # # # """
# # # # # Run one question -> answer -> score round.
# # # # # Usage: python main.py
# # # # # Requires GROQ_API_KEY set in your environment (see .env.example).
# # # # # """

# # # # # from dotenv import load_dotenv
# # # # # load_dotenv()
# # # # # from graph import build_graph
# # # # # from state import initial_state




# # # # # def main():
# # # # #     app = build_graph()
# # # # #     result = app.invoke(initial_state())

# # # # #     print("\n" + "=" * 40)
# # # # #     print(f"Content score: {result['content_score']}/10")
# # # # #     print(f"Feedback: {result['feedback']}")
# # # # #     print("=" * 40)


# # # # # if __name__ == "__main__":
# # # # #     main()
# # # # # """
# # # # # Run one question -> answer -> score round.
# # # # # Usage: python main.py
# # # # # Requires GROQ_API_KEY (and TAVILY_API_KEY, for behavioral questions)
# # # # # set in your environment (see .env.example).
# # # # # """

# # # # # from dotenv import load_dotenv

# # # # # load_dotenv()  # must run before importing graph, since evaluator.py
# # # # #                # creates the Groq client as soon as it's imported

# # # # # from graph import build_graph
# # # # # from state import initial_state
# # # # # from memory.candidate_profile import get_profile, set_profile


# # # # # def _read_multiline(prompt: str) -> str:
# # # # #     print(f"{prompt} (type a line with just ### when you're done, or leave blank + ### to skip):")
# # # # #     lines = []
# # # # #     while True:
# # # # #         line = input()
# # # # #         if line.strip() == "###":
# # # # #             break
# # # # #         lines.append(line)
# # # # #     return "\n".join(lines).strip()


# # # # # def _get_or_collect_profile():
# # # # #     existing = get_profile()
# # # # #     if existing:
# # # # #         print(f"Using saved profile: {existing['company']} — {existing['role']}")
# # # # #         change = input("Use a different company/role/resume this time? (y/n): ").strip().lower()
# # # # #         if change != "y":
# # # # #             return existing

# # # # #     company = input("Target company (e.g. Google, or leave blank): ").strip()
# # # # #     role = input("Target role (e.g. SDE Intern): ").strip()
# # # # #     resume_text = _read_multiline("Paste your resume text")

# # # # #     set_profile(company, role, resume_text)
# # # # #     return {"company": company, "role": role, "resume_text": resume_text}


# # # # # def main():
# # # # #     profile = _get_or_collect_profile()
# # # # #     app = build_graph()
# # # # #     result = app.invoke(
# # # # #         initial_state(
# # # # #             company=profile["company"],
# # # # #             role=profile["role"],
# # # # #             resume_text=profile["resume_text"],
# # # # #         )
# # # # #     )

# # # # #     print("\n" + "=" * 40)
# # # # #     print(f"Content score: {result['content_score']}/10")
# # # # #     print(f"Feedback: {result['feedback']}")
# # # # #     print("=" * 40)


# # # # # if __name__ == "__main__":
# # # # #     main()
# # # # """
# # # # Run one question -> answer -> score round.
# # # # Usage: python main.py
# # # # Requires GROQ_API_KEY (and TAVILY_API_KEY, for behavioral questions)
# # # # set in your environment (see .env.example).
# # # # """

# # # # from dotenv import load_dotenv

# # # # load_dotenv()  # must run before importing graph, since evaluator.py
# # # #                # creates the Groq client as soon as it's imported

# # # # from graph import build_graph
# # # # from state import initial_state
# # # # from memory.candidate_profile import get_profile, set_profile
# # # # from tools.resume_reader import extract_text_from_pdf


# # # # def _read_multiline(prompt: str) -> str:
# # # #     print(f"{prompt} (type a line with just ### when you're done, or leave blank + ### to skip):")
# # # #     lines = []
# # # #     while True:
# # # #         line = input()
# # # #         if line.strip() == "###":
# # # #             break
# # # #         lines.append(line)
# # # #     return "\n".join(lines).strip()


# # # # def _collect_resume() -> str:
# # # #     choice = input("Provide resume as (1) pasted text or (2) PDF file path? [1/2, blank to skip]: ").strip()

# # # #     if choice == "2":
# # # #         path = input("Path to your resume PDF: ").strip()
# # # #         try:
# # # #             text = extract_text_from_pdf(path)
# # # #             print(f"[Extracted {len(text)} characters from PDF]")
# # # #             return text
# # # #         except Exception as e:
# # # #             print(f"[Couldn't read PDF ({e}) — falling back to pasted text]")
# # # #             return _read_multiline("Paste your resume text instead")

# # # #     if choice == "1":
# # # #         return _read_multiline("Paste your resume text")

# # # #     return ""  # skipped


# # # # def _get_or_collect_profile():
# # # #     existing = get_profile()
# # # #     if existing:
# # # #         print(f"Using saved profile: {existing['company']} — {existing['role']}")
# # # #         change = input("Use a different company/role/resume this time? (y/n): ").strip().lower()
# # # #         if change != "y":
# # # #             return existing

# # # #     company = input("Target company (e.g. Google, or leave blank): ").strip()
# # # #     role = input("Target role (e.g. SDE Intern): ").strip()
# # # #     resume_text = _collect_resume()

# # # #     set_profile(company, role, resume_text)
# # # #     return {"company": company, "role": role, "resume_text": resume_text}


# # # # def main():
# # # #     profile = _get_or_collect_profile()
# # # #     app = build_graph()
# # # #     result = app.invoke(
# # # #         initial_state(
# # # #             company=profile["company"],
# # # #             role=profile["role"],
# # # #             resume_text=profile["resume_text"],
# # # #         )
# # # #     )

# # # #     print("\n" + "=" * 40)
# # # #     print(f"Content score: {result['content_score']}/10")
# # # #     print(f"Feedback: {result['feedback']}")
# # # #     print("=" * 40)


# # # # if __name__ == "__main__":
# # # #     main()
# # # """
# # # Run a full interview round: Technical (1 DSA question + 1 resume-based
# # # question) or Behavioral (N HR-style questions in a row).
# # # Usage: python main.py
# # # Requires GROQ_API_KEY (and TAVILY_API_KEY, for behavioral/HR questions)
# # # set in your environment (see .env.example).
# # # """

# # # from dotenv import load_dotenv

# # # load_dotenv()  # must run before importing graph, since evaluator.py
# # #                # creates the Groq client as soon as it's imported

# # # from graph import build_graph
# # # from state import initial_state
# # # from memory.candidate_profile import get_profile, set_profile
# # # from memory.session_store import get_topic_performance
# # # from tools.resume_reader import extract_text_from_pdf
# # # from planner import pick_topic_from
# # # from interviewer import DSA_TOPICS


# # # def _read_multiline(prompt: str) -> str:
# # #     print(f"{prompt} (type a line with just ### when you're done, or leave blank + ### to skip):")
# # #     lines = []
# # #     while True:
# # #         line = input()
# # #         if line.strip() == "###":
# # #             break
# # #         lines.append(line)
# # #     return "\n".join(lines).strip()


# # # def _collect_resume() -> str:
# # #     choice = input("Provide resume as (1) pasted text or (2) PDF file path? [1/2, blank to skip]: ").strip()

# # #     if choice == "2":
# # #         path = input("Path to your resume PDF: ").strip()
# # #         try:
# # #             text = extract_text_from_pdf(path)
# # #             print(f"[Extracted {len(text)} characters from PDF]")
# # #             return text
# # #         except Exception as e:
# # #             print(f"[Couldn't read PDF ({e}) — falling back to pasted text]")
# # #             return _read_multiline("Paste your resume text instead")

# # #     if choice == "1":
# # #         return _read_multiline("Paste your resume text")

# # #     return ""  # skipped


# # # def _get_or_collect_profile():
# # #     existing = get_profile()
# # #     if existing:
# # #         print(f"Using saved profile: {existing['company']} — {existing['role']}")
# # #         change = input("Use a different company/role/resume this time? (y/n): ").strip().lower()
# # #         if change != "y":
# # #             return existing

# # #     company = input("Target company (e.g. Google, or leave blank): ").strip()
# # #     role = input("Target role (e.g. SDE Intern): ").strip()
# # #     resume_text = _collect_resume()

# # #     set_profile(company, role, resume_text)
# # #     return {"company": company, "role": role, "resume_text": resume_text}


# # # def _run_question(app, profile: dict, topic: str, resume_override: str = None) -> dict:
# # #     """Runs one question through the graph. resume_override lets callers
# # #     force resume_text to "" so the behavioral tier-1 resume path is
# # #     skipped (used for the repeated HR questions in a Behavioral round)
# # #     without touching interviewer.py's tiering logic at all."""
# # #     resume_text = profile["resume_text"] if resume_override is None else resume_override
# # #     s = initial_state(company=profile["company"], role=profile["role"], resume_text=resume_text)
# # #     s["question_topic"] = topic
# # #     return app.invoke(s)


# # # def _run_technical_round(app, profile: dict) -> list[dict]:
# # #     dsa_topic = pick_topic_from(list(DSA_TOPICS), get_topic_performance())

# # #     print("\n" + "-" * 40)
# # #     print(f"DSA QUESTION ({dsa_topic})")
# # #     print("-" * 40)
# # #     r1 = _run_question(app, profile, dsa_topic)

# # #     print("\n" + "-" * 40)
# # #     print("RESUME-BASED QUESTION")
# # #     print("-" * 40)
# # #     r2 = _run_question(app, profile, "behavioral")  # full resume_text -> resume tier fires

# # #     return [r1, r2]


# # # def _run_behavioral_round(app, profile: dict) -> list[dict]:
# # #     count_raw = input("How many HR/behavioral questions in this round? [default 3]: ").strip()
# # #     count = int(count_raw) if count_raw.isdigit() and int(count_raw) > 0 else 3

# # #     results = []
# # #     for i in range(count):
# # #         print("\n" + "-" * 40)
# # #         print(f"HR QUESTION {i + 1}/{count}")
# # #         print("-" * 40)
# # #         # resume_override="" skips the resume tier so these are genuine
# # #         # HR/company-style questions, not the same resume story repeated
# # #         r = _run_question(app, profile, "behavioral", resume_override="")
# # #         results.append(r)

# # #     return results


# # # def _print_summary(results: list[dict]) -> None:
# # #     print("\n" + "=" * 40)
# # #     print("ROUND SUMMARY")
# # #     print("=" * 40)
# # #     for i, r in enumerate(results, 1):
# # #         print(f"Q{i} [{r['question_topic']}]: {r['content_score']}/10")
# # #         print(f"   {r['feedback']}")
# # #     print("=" * 40)


# # # def main():
# # #     profile = _get_or_collect_profile()
# # #     app = build_graph()

# # #     round_choice = input("\nInterview round type? (1) Technical  (2) Behavioral: ").strip()
# # #     if round_choice == "2":
# # #         results = _run_behavioral_round(app, profile)
# # #     else:
# # #         results = _run_technical_round(app, profile)

# # #     _print_summary(results)


# # # if __name__ == "__main__":
# # #     main()
# # """
# # Run a full interview round: Technical (1 DSA question + 1 resume-based
# # question) or Behavioral (N HR-style questions in a row).
# # Usage: python main.py
# # Requires GROQ_API_KEY (and TAVILY_API_KEY, for behavioral/HR questions)
# # set in your environment (see .env.example).
# # """

# # from dotenv import load_dotenv

# # load_dotenv()  # must run before importing graph, since evaluator.py
# #                # creates the Groq client as soon as it's imported

# # from graph import build_graph
# # from state import initial_state
# # from memory.candidate_profile import get_profile, set_profile
# # from memory.session_store import get_topic_performance
# # from tools.resume_reader import extract_text_from_pdf
# # from planner import pick_topic_from
# # from interviewer import DSA_TOPICS


# # def _read_multiline(prompt: str) -> str:
# #     print(f"{prompt} (type a line with just ### when you're done, or leave blank + ### to skip):")
# #     lines = []
# #     while True:
# #         line = input()
# #         if line.strip() == "###":
# #             break
# #         lines.append(line)
# #     return "\n".join(lines).strip()


# # def _collect_resume() -> str:
# #     choice = input("Provide resume as (1) pasted text or (2) PDF file path? [1/2, blank to skip]: ").strip()

# #     if choice == "2":
# #         path = input("Path to your resume PDF: ").strip()
# #         try:
# #             text = extract_text_from_pdf(path)
# #             print(f"[Extracted {len(text)} characters from PDF]")
# #             return text
# #         except Exception as e:
# #             print(f"[Couldn't read PDF ({e}) — falling back to pasted text]")
# #             return _read_multiline("Paste your resume text instead")

# #     if choice == "1":
# #         return _read_multiline("Paste your resume text")

# #     return ""  # skipped


# # def _get_or_collect_profile():
# #     existing = get_profile()
# #     if existing:
# #         print(f"Using saved profile: {existing['company']} — {existing['role']}")
# #         change = input("Use a different company/role/resume this time? (y/n): ").strip().lower()
# #         if change != "y":
# #             return existing

# #     company = input("Target company (e.g. Google, or leave blank): ").strip()
# #     role = input("Target role (e.g. SDE Intern): ").strip()
# #     resume_text = _collect_resume()

# #     set_profile(company, role, resume_text)
# #     return {"company": company, "role": role, "resume_text": resume_text}


# # def _run_question(app, profile: dict, topic: str, resume_override: str = None,
# #                    skip_cache: bool = False, avoid_questions: list = None) -> dict:
# #     """Runs one question through the graph. resume_override lets callers
# #     force resume_text to "" so the behavioral tier-1 resume path is
# #     skipped (used for the repeated HR questions in a Behavioral round)
# #     without touching interviewer.py's tiering logic at all. skip_cache
# #     and avoid_questions prevent a round's repeated questions from all
# #     serving the same single cached entry or near-duplicates."""
# #     resume_text = profile["resume_text"] if resume_override is None else resume_override
# #     s = initial_state(company=profile["company"], role=profile["role"], resume_text=resume_text)
# #     s["question_topic"] = topic
# #     s["skip_cache"] = skip_cache
# #     s["avoid_questions"] = avoid_questions or []
# #     return app.invoke(s)


# # def _run_technical_round(app, profile: dict) -> list[dict]:
# #     dsa_topic = pick_topic_from(list(DSA_TOPICS), get_topic_performance())

# #     print("\n" + "-" * 40)
# #     print(f"DSA QUESTION ({dsa_topic})")
# #     print("-" * 40)
# #     r1 = _run_question(app, profile, dsa_topic)

# #     print("\n" + "-" * 40)
# #     print("RESUME-BASED QUESTION")
# #     print("-" * 40)
# #     r2 = _run_question(app, profile, "behavioral")  # full resume_text -> resume tier fires

# #     return [r1, r2]


# # def _run_behavioral_round(app, profile: dict) -> list[dict]:
# #     count_raw = input("How many HR/behavioral questions in this round? [default 3]: ").strip()
# #     count = int(count_raw) if count_raw.isdigit() and int(count_raw) > 0 else 3

# #     results = []
# #     asked_questions = []
# #     for i in range(count):
# #         print("\n" + "-" * 40)
# #         print(f"HR QUESTION {i + 1}/{count}")
# #         print("-" * 40)
# #         # resume_override="" skips the resume tier so these are genuine
# #         # HR/company-style questions, not the same resume story repeated.
# #         # skip_cache + avoid_questions ensure each one is freshly fetched
# #         # and distinct from every question already asked this round.
# #         r = _run_question(
# #             app, profile, "behavioral",
# #             resume_override="",
# #             skip_cache=True,
# #             avoid_questions=asked_questions,
# #         )
# #         results.append(r)
# #         asked_questions.append(r["current_question"])

# #     return results


# # def _print_summary(results: list[dict]) -> None:
# #     print("\n" + "=" * 40)
# #     print("ROUND SUMMARY")
# #     print("=" * 40)
# #     for i, r in enumerate(results, 1):
# #         print(f"Q{i} [{r['question_topic']}]: {r['content_score']}/10")
# #         print(f"   {r['feedback']}")
# #     print("=" * 40)


# # def main():
# #     profile = _get_or_collect_profile()
# #     app = build_graph()

# #     round_choice = input("\nInterview round type? (1) Technical  (2) Behavioral: ").strip()
# #     if round_choice == "2":
# #         results = _run_behavioral_round(app, profile)
# #     else:
# #         results = _run_technical_round(app, profile)

# #     _print_summary(results)


# # if __name__ == "__main__":
# #     main()
# """
# Run a full interview round: Technical (1 DSA question + 1 resume-based
# question) or Behavioral (N HR-style questions in a row).
# Usage: python main.py
# Requires GROQ_API_KEY (and TAVILY_API_KEY, for behavioral/HR questions)
# set in your environment (see .env.example).
# """

# from dotenv import load_dotenv

# load_dotenv()  # must run before importing graph, since evaluator.py
#                # creates the Groq client as soon as it's imported

# from graph import build_graph
# from state import initial_state
# from memory.candidate_profile import get_profile, set_profile
# from memory.session_store import get_topic_performance
# from tools.resume_reader import extract_text_from_pdf
# from planner import pick_topic_from
# from interviewer import DSA_TOPICS


# def _read_multiline(prompt: str) -> str:
#     print(f"{prompt} (type a line with just ### when you're done, or leave blank + ### to skip):")
#     lines = []
#     while True:
#         line = input()
#         if line.strip() == "###":
#             break
#         lines.append(line)
#     return "\n".join(lines).strip()


# def _collect_resume() -> str:
#     choice = input("Provide resume as (1) pasted text or (2) PDF file path? [1/2, blank to skip]: ").strip()

#     if choice == "2":
#         path = input("Path to your resume PDF: ").strip()
#         try:
#             text = extract_text_from_pdf(path)
#             print(f"[Extracted {len(text)} characters from PDF]")
#             return text
#         except Exception as e:
#             print(f"[Couldn't read PDF ({e}) — falling back to pasted text]")
#             return _read_multiline("Paste your resume text instead")

#     if choice == "1":
#         return _read_multiline("Paste your resume text")

#     return ""  # skipped


# def _get_or_collect_profile():
#     existing = get_profile()
#     if existing:
#         print(f"Using saved profile: {existing['company']} — {existing['role']}")
#         change = input("Use a different company/role/resume this time? (y/n): ").strip().lower()
#         if change != "y":
#             return existing

#     company = input("Target company (e.g. Google, or leave blank): ").strip()
#     role = input("Target role (e.g. SDE Intern): ").strip()
#     resume_text = _collect_resume()

#     set_profile(company, role, resume_text)
#     return {"company": company, "role": role, "resume_text": resume_text}


# def _run_question(app, profile: dict, topic: str, resume_override: str = None,
#                    skip_cache: bool = False, avoid_questions: list = None) -> dict:
#     """Runs one question through the graph. resume_override lets callers
#     force resume_text to "" so the behavioral tier-1 resume path is
#     skipped (used for the repeated HR questions in a Behavioral round)
#     without touching interviewer.py's tiering logic at all. skip_cache
#     and avoid_questions prevent a round's repeated questions from all
#     serving the same single cached entry or near-duplicates."""
#     resume_text = profile["resume_text"] if resume_override is None else resume_override
#     s = initial_state(company=profile["company"], role=profile["role"], resume_text=resume_text)
#     s["question_topic"] = topic
#     s["skip_cache"] = skip_cache
#     s["avoid_questions"] = avoid_questions or []
#     return app.invoke(s)


# def _run_technical_round(app, profile: dict) -> list[dict]:
#     dsa_topic = pick_topic_from(list(DSA_TOPICS), get_topic_performance())

#     print("\n" + "-" * 40)
#     print(f"DSA QUESTION ({dsa_topic})")
#     print("-" * 40)
#     r1 = _run_question(app, profile, dsa_topic)

#     print("\n" + "-" * 40)
#     print("RESUME-BASED QUESTION")
#     print("-" * 40)
#     r2 = _run_question(app, profile, "behavioral")  # full resume_text -> resume tier fires

#     return [r1, r2]


# def _run_behavioral_round(app, profile: dict) -> list[dict]:
#     count_raw = input("How many HR/behavioral questions in this round? [default 3]: ").strip()
#     count = int(count_raw) if count_raw.isdigit() and int(count_raw) > 0 else 3

#     results = []
#     asked_questions = []
#     for i in range(count):
#         print("\n" + "-" * 40)
#         print(f"HR QUESTION {i + 1}/{count}")
#         print("-" * 40)
#         # resume_override="" skips the resume tier so these are genuine
#         # HR/company-style questions, not the same resume story repeated.
#         # skip_cache + avoid_questions ensure each one is freshly fetched
#         # and distinct from every question already asked this round.
#         r = _run_question(
#             app, profile, "behavioral",
#             resume_override="",
#             skip_cache=True,
#             avoid_questions=asked_questions,
#         )
#         results.append(r)
#         asked_questions.append(r["current_question"])

#     return results


# def _print_summary(results: list[dict]) -> None:
#     print("\n" + "=" * 40)
#     print("ROUND SUMMARY")
#     print("=" * 40)
#     for i, r in enumerate(results, 1):
#         print(f"Q{i} [{r['question_topic']}]: Content {r['content_score']}/10")
#         print(f"   {r['feedback']}")
#         if r.get("communication_score") is not None:
#             print(f"   Communication: {r['communication_score']}/10 — {r['communication_feedback']}")
#     print("=" * 40)


# def main():
#     profile = _get_or_collect_profile()
#     app = build_graph()

#     round_choice = input("\nInterview round type? (1) Technical  (2) Behavioral: ").strip()
#     if round_choice == "2":
#         results = _run_behavioral_round(app, profile)
#     else:
#         results = _run_technical_round(app, profile)

#     _print_summary(results)


# if __name__ == "__main__":
#     main()
"""
Run a full interview round: Technical (1 DSA question + 1 resume-based
question) or Behavioral (N HR-style questions in a row).
Usage: python main.py
Requires GROQ_API_KEY (and TAVILY_API_KEY, for behavioral/HR questions)
set in your environment (see .env.example).
"""

from dotenv import load_dotenv

load_dotenv()  # must run before importing graph, since evaluator.py
               # creates the Groq client as soon as it's imported

from graph import build_graph
from state import initial_state
from memory.candidate_profile import get_profile, set_profile
from memory.session_store import get_topic_performance
from tools.resume_reader import extract_text_from_pdf
from planner import pick_topic_from
from interviewer import DSA_TOPICS
from memory.asked_resume_questions import get_asked_resume_questions, add_asked_resume_question


def _read_multiline(prompt: str) -> str:
    print(f"{prompt} (type a line with just ### when you're done, or leave blank + ### to skip):")
    lines = []
    while True:
        line = input()
        if line.strip() == "###":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def _collect_resume() -> str:
    choice = input("Provide resume as (1) pasted text or (2) PDF file path? [1/2, blank to skip]: ").strip()

    if choice == "2":
        path = input("Path to your resume PDF: ").strip()
        try:
            text = extract_text_from_pdf(path)
            print(f"[Extracted {len(text)} characters from PDF]")
            return text
        except Exception as e:
            print(f"[Couldn't read PDF ({e}) — falling back to pasted text]")
            return _read_multiline("Paste your resume text instead")

    if choice == "1":
        return _read_multiline("Paste your resume text")

    return ""  # skipped


def _get_or_collect_profile():
    existing = get_profile()
    if existing:
        print(f"Using saved profile: {existing['company']} — {existing['role']}")
        change = input("Use a different company/role/resume this time? (y/n): ").strip().lower()
        if change != "y":
            return existing

    company = input("Target company (e.g. Google, or leave blank): ").strip()
    role = input("Target role (e.g. SDE Intern): ").strip()
    resume_text = _collect_resume()

    set_profile(company, role, resume_text)
    return {"company": company, "role": role, "resume_text": resume_text}


def _run_question(app, profile: dict, topic: str, resume_override: str = None,
                   skip_cache: bool = False, avoid_questions: list = None) -> dict:
    """Runs one question through the graph. resume_override lets callers
    force resume_text to "" so the behavioral tier-1 resume path is
    skipped (used for the repeated HR questions in a Behavioral round)
    without touching interviewer.py's tiering logic at all. skip_cache
    and avoid_questions prevent a round's repeated questions from all
    serving the same single cached entry or near-duplicates."""
    resume_text = profile["resume_text"] if resume_override is None else resume_override
    s = initial_state(company=profile["company"], role=profile["role"], resume_text=resume_text)
    s["question_topic"] = topic
    s["skip_cache"] = skip_cache
    s["avoid_questions"] = avoid_questions or []
    return app.invoke(s)


def _run_technical_round(app, profile: dict) -> list[dict]:
    dsa_topic = pick_topic_from(list(DSA_TOPICS), get_topic_performance())

    print("\n" + "-" * 40)
    print(f"DSA QUESTION ({dsa_topic})")
    print("-" * 40)
    r1 = _run_question(app, profile, dsa_topic)

    print("\n" + "-" * 40)
    print("RESUME-BASED QUESTION")
    print("-" * 40)
    # avoid_questions is seeded from every resume question asked in past runs
    # too, not just this round — otherwise the generator keeps landing on the
    # same salient resume detail (e.g. the same architecture decision) run
    # after run, since a single Technical round only ever asks one of these.
    past_resume_questions = get_asked_resume_questions()
    r2 = _run_question(
        app, profile, "behavioral", avoid_questions=past_resume_questions
    )  # full resume_text -> resume tier fires
    add_asked_resume_question(r2["current_question"])

    return [r1, r2]


def _run_behavioral_round(app, profile: dict) -> list[dict]:
    count_raw = input("How many HR/behavioral questions in this round? [default 3]: ").strip()
    count = int(count_raw) if count_raw.isdigit() and int(count_raw) > 0 else 3

    results = []
    asked_questions = []
    for i in range(count):
        print("\n" + "-" * 40)
        print(f"HR QUESTION {i + 1}/{count}")
        print("-" * 40)
        # resume_override="" skips the resume tier so these are genuine
        # HR/company-style questions, not the same resume story repeated.
        # skip_cache + avoid_questions ensure each one is freshly fetched
        # and distinct from every question already asked this round.
        r = _run_question(
            app, profile, "behavioral",
            resume_override="",
            skip_cache=True,
            avoid_questions=asked_questions,
        )
        results.append(r)
        asked_questions.append(r["current_question"])

    return results


def _print_summary(results: list[dict]) -> None:
    print("\n" + "=" * 40)
    print("ROUND SUMMARY")
    print("=" * 40)
    for i, r in enumerate(results, 1):
        print(f"Q{i} [{r['question_topic']}]: Content {r['content_score']}/10")
        print(f"   {r['feedback']}")
        if r.get("communication_score") is not None:
            print(f"   Communication: {r['communication_score']}/10 — {r['communication_feedback']}")
    print("=" * 40)


def main():
    profile = _get_or_collect_profile()
    app = build_graph()

    round_choice = input("\nInterview round type? (1) Technical  (2) Behavioral: ").strip()
    if round_choice == "2":
        results = _run_behavioral_round(app, profile)
    else:
        results = _run_technical_round(app, profile)

    _print_summary(results)


if __name__ == "__main__":
    main()