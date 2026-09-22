from backend.parsers.judgment_parser import parse_judgment
from backend.parsers.contract_parser import parse_contract


def parse_document(text: str, document_type: str):

    if document_type == "COURT_JUDGMENT":
        return parse_judgment(text)

    if document_type == "CONTRACT":
        return parse_contract(text)

    return {}