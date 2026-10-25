# """
# Runs submitted code via Judge0 CE's free public instance (ce.judge0.com,
# no API key needed, rate-limited). Returns real stdout/stderr/status.

# Uses base64_encoded=true: sending source_code as plain text intermittently
# returned a bare 400 with no error body — a known, long-standing quirk of
# public Judge0 instances with certain characters in the code (confirmed
# against a real C++ submission during testing). Base64-encoding both the
# request and the response fields is the documented, reliable way around it.

# Known limitation: Codeforces' API only gives us problem metadata, not
# official test cases, so this doesn't auto-diff against a hidden test
# suite the way a real judge would. It runs the code as-submitted (with
# whatever stdin the candidate provides, if any) and reports exactly
# what happened — the Evaluator treats that as ground truth over the
# candidate's own description of what their code does.
# """

# import base64
# import requests

# _LANGUAGE_IDS = {
#     "python": 71,
#     "cpp": 54,
#     "java": 62,
#     "javascript": 63,
# }

# _JUDGE0_URL = "https://ce.judge0.com/submissions"

# # LeetCode's editor silently pre-includes these for you; Judge0 doesn't.
# # Prepending them (harmless if the candidate already has their own
# # includes — duplicate #includes are a no-op in C++) removes the most
# # common friction: "missing vector/queue/namespace" errors that have
# # nothing to do with the candidate's actual algorithm.
# _CPP_PRELUDE = "#include <bits/stdc++.h>\nusing namespace std;\n\n"


# def _prepare_source(source_code: str, language: str) -> str:
#     if language.lower() == "cpp":
#         return _CPP_PRELUDE + source_code
#     return source_code


# def _b64_encode(text: str) -> str:
#     return base64.b64encode(text.encode("utf-8")).decode("ascii")


# def _b64_decode(text) -> str:
#     if not text:
#         return ""
#     return base64.b64decode(text).decode("utf-8", errors="replace")


# def run_code(source_code: str, language: str, stdin: str = "") -> dict:
#     language_id = _LANGUAGE_IDS.get(language.lower())
#     if language_id is None:
#         raise ValueError(
#             f"Unsupported language '{language}'. Choose from: {list(_LANGUAGE_IDS)}"
#         )

#     prepared_source = _prepare_source(source_code, language)

#     resp = requests.post(
#         _JUDGE0_URL,
#         params={"base64_encoded": "true", "wait": "true"},
#         json={
#             "source_code": _b64_encode(prepared_source),
#             "language_id": language_id,
#             "stdin": _b64_encode(stdin) if stdin else "",
#         },
#         timeout=20,
#     )
#     resp.raise_for_status()
#     data = resp.json()

#     return {
#         "stdout": _b64_decode(data.get("stdout")).strip(),
#         "stderr": _b64_decode(data.get("stderr")).strip(),
#         "compile_output": _b64_decode(data.get("compile_output")).strip(),
#         "status": data.get("status", {}).get("description", "Unknown"),
#     }
"""
Runs submitted code via Judge0 CE's free public instance (ce.judge0.com,
no API key needed, rate-limited). Returns real stdout/stderr/status.

Uses base64_encoded=true: sending source_code as plain text intermittently
returned a bare 400 with no error body — a known, long-standing quirk of
public Judge0 instances with certain characters in the code (confirmed
against a real C++ submission during testing). Base64-encoding both the
request and the response fields is the documented, reliable way around it.

Known limitation: Codeforces' API only gives us problem metadata, not
official test cases, so this doesn't auto-diff against a hidden test
suite the way a real judge would. It runs the code as-submitted (with
whatever stdin the candidate provides, if any) and reports exactly
what happened — the Evaluator treats that as ground truth over the
candidate's own description of what their code does.
"""

import base64
import requests

_LANGUAGE_IDS = {
    "python": 71,
    "cpp": 54,
    "java": 62,
    "javascript": 63,
}

_JUDGE0_URL = "https://ce.judge0.com/submissions"

# LeetCode's editor silently pre-includes these for you; Judge0 doesn't.
# Prepending them (harmless if the candidate already has their own
# includes — duplicate #includes are a no-op in C++) removes the most
# common friction: "missing vector/queue/namespace" errors that have
# nothing to do with the candidate's actual algorithm.
_CPP_PRELUDE = "#include <bits/stdc++.h>\nusing namespace std;\n\n"


def _prepare_source(source_code: str, language: str) -> str:
    if language.lower() == "cpp":
        return _CPP_PRELUDE + source_code
    return source_code


def _b64_encode(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def _b64_decode(text) -> str:
    if not text:
        return ""
    return base64.b64decode(text).decode("utf-8", errors="replace")


def run_code(source_code: str, language: str, stdin: str = "") -> dict:
    language_id = _LANGUAGE_IDS.get(language.lower())
    if language_id is None:
        raise ValueError(
            f"Unsupported language '{language}'. Choose from: {list(_LANGUAGE_IDS)}"
        )

    prepared_source = _prepare_source(source_code, language)

    resp = requests.post(
        _JUDGE0_URL,
        params={"base64_encoded": "true", "wait": "true"},
        json={
            "source_code": _b64_encode(prepared_source),
            "language_id": language_id,
            "stdin": _b64_encode(stdin) if stdin else "",
        },
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()

    return {
        "stdout": _b64_decode(data.get("stdout")).strip(),
        "stderr": _b64_decode(data.get("stderr")).strip(),
        "compile_output": _b64_decode(data.get("compile_output")).strip(),
        "status": data.get("status", {}).get("description", "Unknown"),
    }