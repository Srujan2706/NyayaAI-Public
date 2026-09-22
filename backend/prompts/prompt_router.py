from backend.prompts.judgment_prompt import JUDGMENT_PROMPT
from backend.prompts.act_prompt import ACT_PROMPT
from backend.prompts.contract_prompt import CONTRACT_PROMPT
from backend.prompts.notice_prompt import NOTICE_PROMPT


def get_prompt(document_type):

    document_type = document_type.lower()

    if "judgment" in document_type:
        return JUDGMENT_PROMPT

    if "act" in document_type:
        return ACT_PROMPT

    if "contract" in document_type:
        return CONTRACT_PROMPT

    if "notice" in document_type:
        return NOTICE_PROMPT

    return JUDGMENT_PROMPT