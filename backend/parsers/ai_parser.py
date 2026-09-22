import json
import ollama

from backend.utils.config import OLLAMA_MODEL
from backend.prompts.prompt_router import get_prompt

MODEL = OLLAMA_MODEL


def parse_document(text: str, document_type: str = "Unknown"):

    base_prompt = get_prompt(document_type)

    prompt = f"""
{base_prompt}

Document:

{text[:12000]}
"""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = response["message"]["content"]

    try:

        start = answer.index("{")
        end = answer.rindex("}") + 1

        data = json.loads(answer[start:end])

        # Ensure document type is always present
        data["document_type"] = document_type

        return data

    except Exception:

        return {

            "document_type": document_type,

            "summary": answer,

            "facts": "",

            "issues": "",

            "arguments": "",

            "reasoning": "",

            "decision": "",

            "important_sections": [],

            "important_people": [],

            "important_dates": []
        }


if __name__ == "__main__":

    while True:

        path = input("\nText File : ")

        if path.lower() == "exit":
            break

        with open(path, encoding="utf-8") as f:
            text = f.read()

        doc_type = input("Document Type (Judgment / Act / Contract / Notice): ")

        result = parse_document(
            text,
            doc_type
        )

        print(json.dumps(
            result,
            indent=4,
            ensure_ascii=False
        ))