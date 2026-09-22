from typing import Optional


GENERAL_RESPONSES = {

    # Greetings
    "hello":
        "Hello! I'm NyayaAI. How can I assist you with Indian laws or legal documents today?",

    "hi":
        "Hi! I'm NyayaAI. Ask me about Indian laws or upload a legal document for analysis.",

    "hey":
        "Hello! What legal question can I help you with?",

    # Thanks

    "thanks":
        "You're welcome!",

    "thank you":
        "You're welcome! Happy to help.",

    # Goodbye

    "bye":
        "Goodbye! Have a great day.",

    # About

    "who are you":
        "I am NyayaAI, an AI-powered Indian Legal Assistant designed for legal research, document analysis and explainable question answering.",

    "what can you do":
        "I can answer questions about Indian laws, analyze uploaded legal documents, summarize judgments, explain legal provisions, and provide evidence-backed answers.",

    # Laws

    "what is bns":
        "BNS stands for Bharatiya Nyaya Sanhita, 2023. It replaced the Indian Penal Code (IPC).",

    "what is bnss":
        "BNSS stands for Bharatiya Nagarik Suraksha Sanhita, 2023. It replaced the Code of Criminal Procedure (CrPC).",

    "what is bsa":
        "BSA stands for Bharatiya Sakshya Adhiniyam, 2023. It replaced the Indian Evidence Act, 1872.",

    # Abuse

    "fuck you":
        "I'm here to help with legal questions whenever you're ready.",

    "idiot":
        "Let's keep the conversation focused. How can I help with your legal question?",

    "stupid":
        "I'm here to assist you with Indian law and legal documents."

}


def answer_general_query(question: str) -> Optional[str]:

    q = question.lower().strip()

    for key, value in GENERAL_RESPONSES.items():

        if key in q:

            return value

    return None