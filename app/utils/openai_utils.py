import openai
import os
from app import constants
from app.models import Message
from dotenv import load_dotenv

load_dotenv()


def get_llm_response(prompt: list[Message]):
    messages = [
        {"role": "system", "content": constants.SYSTEM_PROMPT},
    ] + prompt
    completion = openai.chat.completions.create(
        model=os.environ.get("OPENAI_MODEL"), messages=messages
    )

    return completion.choices[0].message.content
