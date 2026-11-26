import os
import base64
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

MODEL = "google/gemini-4-hydrogen"
SYSTEM_PROMPT = (
    "You are a friendly assistant on Telegram. "
    "Keep answers short and simple, like a chat message. "
    "Use plain text, no markdown."
)

histories = {}


def ask(chat_id, text, image_bytes=None):
    history = histories.setdefault(chat_id, [])

    if image_bytes:
        b64 = base64.b64encode(image_bytes).decode()
        content = [
            {"type": "text", "text": text},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
        ]
    else:
        content = text

    history.append({"role": "user", "content": content})
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history[-20:]

    response = client.chat.completions.create(model=MODEL, messages=messages)
    answer = response.choices[0].message.content
    history.append({"role": "assistant", "content": answer})
    return answer


def reset(chat_id):
    histories.pop(chat_id, None)


if __name__ == "__main__":
    print(ask(1, "My name is Rahul. Suggest one quick breakfast."))
    print(ask(1, "What is my name?"))
    print(ask(2, "What is my name?"))
