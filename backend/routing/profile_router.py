import json
from pathlib import Path

from backend.utils.config import DYNAMIC_PROFILES


def load_latest_profile():

    files = sorted(
        Path(DYNAMIC_PROFILES).glob("*_profile.json"),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )

    if not files:
        return None

    with open(files[0], encoding="utf-8") as f:
        return json.load(f)


def answer_from_profile(intent):

    profile = load_latest_profile()

    if profile is None:
        return None

    if intent == "summary":
        return profile.get("summary")

    if intent == "decision":
        return profile.get("decision")

    if intent == "facts":
        return "\n".join(profile.get("facts", []))

    if intent == "issues":
        return "\n".join(profile.get("issues", []))

    if intent == "court":
        return profile.get("court")

    if intent == "judge":
        return profile.get("judge")

    if intent == "case_number":
        return profile.get("case_number")

    if intent == "reasoning":
        return profile.get("reasoning")

    return None