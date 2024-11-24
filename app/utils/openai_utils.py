import openai
import os
import base64
from app import constants
from app.models import Role, GeneratedQuestionList
from dotenv import load_dotenv
from typing import List


load_dotenv()


def _encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def get_generated_questions_and_answers(question_details: str, image_filepath: str):
    base64_image = _encode_image(image_filepath)
    # TODO: update the system prompt to generate a specific number of questions defined by the original user query (currently it is hardcoded to 5)
    messages = [
        {"role": Role.SYSTEM, "content": constants.SYSTEM_PROMPT_GENERATE_QUESTIONS},
        {
            "role": Role.USER,
            "content": [
                {
                    "type": "text",
                    "text": question_details,
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                },
            ],
        },
    ]

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
