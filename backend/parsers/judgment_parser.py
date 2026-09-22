import re


def extract(pattern, text):

    m = re.search(
        pattern,
        text,
        re.IGNORECASE | re.DOTALL
    )

    if m:
        return m.group(1).strip()

    return ""


def parse_judgment(text: str):

    data = {}

    upper = text.upper()

    # -------------------------------------------------------
    # Court
    # -------------------------------------------------------

    m = re.search(
        r"IN THE (.*?)\n",
        text,
        re.IGNORECASE
    )

    data["court"] = m.group(1).strip() if m else ""

    # -------------------------------------------------------
    # Date
    # -------------------------------------------------------

    m = re.search(
        r"DATED[: ]+([0-9\-\.]+)",
        text,
        re.IGNORECASE
    )

    data["date"] = m.group(1) if m else ""

    # -------------------------------------------------------
    # Judge
    # -------------------------------------------------------

    m = re.search(
        r"CORAM(.*?)CRP",
        text,
        re.DOTALL | re.IGNORECASE
    )

    if m:

        judge = m.group(1)

        judge = re.sub(
            r"\s+",
            " ",
            judge
        )

        data["judge"] = judge.strip()

    else:

        data["judge"] = ""

    # -------------------------------------------------------
    # Case Number
    # -------------------------------------------------------

    m = re.search(
        r"(CRP\s+No\.\s*.*)",
        text,
        re.IGNORECASE
    )

    data["case_number"] = m.group(1).strip() if m else ""

    # -------------------------------------------------------
    # Petitioners
    # -------------------------------------------------------

    m = re.search(
        r"CRP.*?\n(.*?)\.\.Petitioner",
        text,
        re.DOTALL | re.IGNORECASE
    )

    data["petitioners"] = m.group(1).strip() if m else ""

    # -------------------------------------------------------
    # Respondents
    # -------------------------------------------------------

    m = re.search(
        r"Vs(.*?)\.\.Respondent",
        text,
        re.DOTALL | re.IGNORECASE
    )

    data["respondents"] = m.group(1).strip() if m else ""

    # -------------------------------------------------------
    # Prayer
    # -------------------------------------------------------

    m = re.search(
        r"Prayer\s*:(.*?)For Petitioner",
        text,
        re.DOTALL | re.IGNORECASE
    )

    data["prayer"] = m.group(1).strip() if m else ""

    # -------------------------------------------------------
    # ORDER
    # -------------------------------------------------------

    order = ""

    m = re.search(
        r"ORDER(.*)",
        text,
        re.DOTALL | re.IGNORECASE
    )

    if m:

        order = m.group(1)

    # -------------------------------------------------------
    # Facts
    # -------------------------------------------------------

    m = re.search(
        r"2\.(.*?)3\.",
        order,
        re.DOTALL
    )

    data["facts"] = m.group(1).strip() if m else ""

    # -------------------------------------------------------
    # Arguments
    # -------------------------------------------------------

    m = re.search(
        r"3\.(.*?)4\.",
        order,
        re.DOTALL
    )

    data["arguments"] = m.group(1).strip() if m else ""

    # -------------------------------------------------------
    # Reasoning
    # -------------------------------------------------------

    m = re.search(
        r"4\.(.*?)5\.",
        order,
        re.DOTALL
    )

    data["reasoning"] = m.group(1).strip() if m else ""

    # -------------------------------------------------------
    # Decision
    # -------------------------------------------------------

    m = re.search(
        r"5\.(.*)",
        order,
        re.DOTALL
    )

    data["decision"] = m.group(1).strip() if m else ""

    return data