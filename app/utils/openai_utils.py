import openai
import os
import base64
import json
from app import constants
from app.models import (
    Role,
    GeneratedQuestion,
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


def get_generated_questions_and_answers(
    topic: str,
    sub_topic: str,
    image_filepaths: List[str],
    is_plain_text: bool = False,
    use_image: bool = True,
    questions: List[str] = [],  # will be empty if use_image is True
    use_few_shot: bool = False,
) -> GeneratedQuestion:
    print(f"use_image: {use_image}, use_few_shot: {use_few_shot}")
    if use_image:
        system_prompt = constants.SYSTEM_PROMPT_GENERATE_QUESTIONS_IMAGE
        question_details = f"<topic>{topic}</topic>\n<sub_topic>{sub_topic}</sub_topic>"
        user_content = [
            {
                "type": "text",
                "text": question_details,
            }
        ]
        print(f"user_content_image: {user_content}")
        print(f"image_filepaths: {image_filepaths}")
        for _, img_filepath in enumerate(image_filepaths):
            base64_image = _encode_image(img_filepath)
            image_name = os.path.basename(img_filepath)
            user_content += [
                {
                    "type": "text",
                    "text": f"<image_name>{image_name}</image_name>",
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                },
            ]
        print(f"Len(image_filepaths): {len(image_filepaths)}")
        # is_plain_text flag was only tested with image questions
        # i.e. there is no plain text system prompt for textual questions
        if is_plain_text:
            system_prompt = constants.SYSTEM_PROMPT_GENERATE_QUESTIONS_IMAGE_PLAIN_TEXT
    else:
        system_prompt = constants.SYSTEM_PROMPT_GENERATE_QUESTIONS
        user_content = f""
        for i, qn in enumerate(questions):
            user_content += f"<question>Question {i + 1}: {qn}</question>"
        user_content += f"<topic>{topic}</topic>\n<sub_topic>{sub_topic}</sub_topic>"
        print(f"user_content_text: {user_content}")

    if use_few_shot:
        print(f"Using few-shot examples for sub-topic: {sub_topic}")
        # load json file with few-shot examples
        with open("app/data/few_shot_examples.json", "r") as f:
            few_shot_examples = json.load(f)
        if sub_topic in few_shot_examples:
            few_shot_examples_for_sub_topic = few_shot_examples[sub_topic]
            example_question = few_shot_examples_for_sub_topic["question"]
            example_answer = few_shot_examples_for_sub_topic["answer"]
            system_prompt += f"\n\nExample question:\n{example_question}\n\nExample answer:\n{example_answer}"

    messages = [
        {"role": Role.SYSTEM, "content": system_prompt},
        {"role": Role.USER, "content": user_content},
    ]

    # Generate completion using OpenAI API
    completion = openai.beta.chat.completions.parse(
        model=os.environ.get("OPENAI_MODEL"),
        messages=messages,
        response_format=GeneratedQuestion,
    )

    # Return the parsed response containing generated questions
    return completion.choices[0].message.parsed


def get_python_script_and_answer(question_text: str, suggested_answer: str) -> str:
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
        max_completion_tokens=2500,
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
