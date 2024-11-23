import openai
import os
from app import constants
from app.models import Message, Role, GeneratedQuestionList
from dotenv import load_dotenv
from typing import List


load_dotenv()


def get_llm_response(prompt: list[Message]):
    messages = [
        {"role": Role.SYSTEM, "content": constants.SYSTEM_PROMPT},
    ] + prompt
    completion = openai.chat.completions.create(
        model=os.environ.get("OPENAI_MODEL"), messages=messages
    )

    return completion.choices[0].message.content


def get_generated_questions_and_answers(prompt: list[Message]):
    messages = [
        {"role": Role.SYSTEM, "content": constants.SYSTEM_PROMPT_GENERATE_QUESTIONS},
    ] + prompt

    completion = openai.beta.chat.completions.parse(
        model=os.environ.get("OPENAI_MODEL"),
        messages=messages,
        response_format=GeneratedQuestionList,
    )

    return completion.choices[0].message.parsed


def get_embedding(text: str, model="text-embedding-3-small") -> List[float]:
    """Get embedding for a given text using OpenAI's API"""
    try:

        response = openai.embeddings.create(input=text, model=model)
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return None
