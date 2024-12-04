import openai
import os
import base64
from app import constants
from app.models import (
    Role,
    GeneratedQuestionList,
    GeneratedPythonScript,
    CorrectedGeneratedPythonScript,
    FormattedGeneratedPythonScript,
)
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


def get_python_script_and_answer(
    question_text: str, suggested_answer: str
) -> GeneratedPythonScript:
    user_content = f"<question>{question_text}</question>\n<suggested_answer>{suggested_answer}</suggested_answer>"
    messages = [
        {
            "role": Role.SYSTEM,
            "content": constants.SYSTEM_PROMPT_GENERATE_PYTHON_SCRIPT,
        },
        {"role": Role.USER, "content": user_content},
    ]

    completion = openai.beta.chat.completions.parse(
        model=os.environ.get("OPENAI_MODEL"),
        messages=messages,
        response_format=GeneratedPythonScript,
        temperature=0.2,
        top_p=0.2,
    )

    return completion.choices[0].message.parsed


def get_corrected_python_script(
    question_text: str, suggested_answer: str, previous_script: str, error_message: str
) -> CorrectedGeneratedPythonScript:
    user_content = f"<question>{question_text}</question>\n<suggested_answer>{suggested_answer}</suggested_answer>\n<script>{previous_script}</script>\n<error>{error_message}</error>"
    messages = [
        {
            "role": Role.SYSTEM,
            "content": constants.SYSTEM_PROMPT_DEBUG,
        },
        {"role": Role.USER, "content": user_content},
    ]

    completion = openai.beta.chat.completions.parse(
        model=os.environ.get("OPENAI_MODEL"),
        messages=messages,
        response_format=CorrectedGeneratedPythonScript,
        temperature=0.2,
        top_p=0.2,
    )

    return completion.choices[0].message.parsed


def get_format_matched_script(
    question_text: str,
    suggested_answer: str,
    previous_script: str,
    computed_answer: str,
) -> FormattedGeneratedPythonScript:
    user_content = f"<question>{question_text}</question>\n<suggested_answer>{suggested_answer}</suggested_answer>\n<script>{previous_script}</script>\n<computed_answer>{computed_answer}</computed_answer>"
    print(f"user_content: {user_content}")
    messages = [
        {
            "role": Role.SYSTEM,
            "content": constants.SYSTEM_PROMPT_FORMAT_PYTHON_SCRIPT_OUTPUT,
        },
        {"role": Role.USER, "content": user_content},
    ]

    completion = openai.beta.chat.completions.parse(
        model=os.environ.get("OPENAI_MODEL"),
        messages=messages,
        response_format=FormattedGeneratedPythonScript,
        temperature=0.2,
        top_p=0.2,
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
