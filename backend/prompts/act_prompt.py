ACT_PROMPT = """
You are an Indian Legal AI.

Analyze this Act.

Return ONLY JSON.

Schema:

{
    "document_type":"Act",

    "act_name":"",

    "purpose":"",

    "chapters":[],

    "important_sections":[],

    "definitions":[],

    "penalties":[],

    "summary":""
}

Rules:

1. Don't hallucinate.
2. Use only the supplied text.
3. Return JSON only.
"""