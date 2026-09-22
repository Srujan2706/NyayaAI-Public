import re


def classify_query(question: str) -> str:

    q = question.lower().strip()

    summary = [
        "summary",
        "summarize",
        "overview",
        "gist",
        "brief"
    ]

    decision = [
        "decision",
        "judgement",
        "judgment",
        "final order",
        "who won",
        "result",
        "outcome"
    ]

    facts = [
        "facts",
        "background",
        "case facts"
    ]

    issues = [
        "issues",
        "questions involved",
        "legal issues"
    ]

    reasoning = [
        "reasoning",
        "analysis",
        "why",
        "explain reasoning"
    ]

    court = [
        "court",
        "which court"
    ]

    judge = [
        "judge",
        "justice"
    ]

    case_number = [
        "case number",
        "petition number",
        "crp",
        "appeal number"
    ]

    for word in summary:
        if word in q:
            return "summary"

    for word in decision:
        if word in q:
            return "decision"

    for word in facts:
        if word in q:
            return "facts"

    for word in issues:
        if word in q:
            return "issues"

    for word in reasoning:
        if word in q:
            return "reasoning"

    for word in court:
        if word in q:
            return "court"

    for word in judge:
        if word in q:
            return "judge"

    for word in case_number:
        if word in q:
            return "case_number"

    return "general"