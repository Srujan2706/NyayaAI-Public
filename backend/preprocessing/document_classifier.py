import re


def detect_document_type(text: str) -> str:

    t = text.upper()

    # --------------------------------------------------
    # Court Judgment
    # --------------------------------------------------

    if (
        "SUPREME COURT OF INDIA" in t
        or "HIGH COURT" in t
        or "VERSUS" in t
        or "V." in t
        or "JUDGMENT" in t
    ):
        return "COURT_JUDGMENT"

    # --------------------------------------------------
    # Acts
    # --------------------------------------------------

    if (
        "BE IT ENACTED" in t
        or "AN ACT" in t
        or "SHORT TITLE" in t
        or "CHAPTER I" in t
        or re.search(r"SECTION\s+\d+", t)
    ):
        return "ACT"

    # --------------------------------------------------
    # Contract
    # --------------------------------------------------

    if (
        "THIS AGREEMENT" in t
        or "NOW THEREFORE" in t
        or "PARTIES" in t
        or "IN WITNESS WHEREOF" in t
    ):
        return "CONTRACT"

    # --------------------------------------------------
    # FIR
    # --------------------------------------------------

    if (
        "FIRST INFORMATION REPORT" in t
        or "FIR NO" in t
    ):
        return "FIR"

    # --------------------------------------------------
    # Legal Notice
    # --------------------------------------------------

    if (
        "LEGAL NOTICE" in t
        or "YOU ARE HEREBY CALLED UPON" in t
    ):
        return "LEGAL_NOTICE"

    # --------------------------------------------------

    return "UNKNOWN"


if __name__ == "__main__":

    from extractor_api import extract_pdf

    while True:

        pdf = input("PDF : ")

        if pdf.lower() == "exit":
            break

        text = extract_pdf(pdf)

        print(detect_document_type(text))