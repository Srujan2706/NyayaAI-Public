from collections import deque

MAX_HISTORY = 10

_history = deque(maxlen=MAX_HISTORY)


def add_message(role, content):

    _history.append({
        "role": role,
        "content": content
    })


def get_history():

    return list(_history)


def clear_history():

    _history.clear()


def build_history():

    if not _history:
        return ""

    text = ""

    for msg in _history:

        role = msg["role"].upper()

        text += f"{role}: {msg['content']}\n\n"

    return text