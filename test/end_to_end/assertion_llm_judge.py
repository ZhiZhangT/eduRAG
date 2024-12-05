import os
import sys
import openai
from typing import Dict, Union, Any
from dotenv import load_dotenv
from pydantic import BaseModel

# Get the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory of the current directory
parent_dir = os.path.dirname(current_dir)
# Get the parent directory of the parent directory (which should contain 'app')
grandparent_dir = os.path.dirname(parent_dir)
# Add the grandparent directory to sys.path
sys.path.append(grandparent_dir)
import app.constants as constants
from app.models import Role

load_dotenv()


class IsAnswerCorrect(BaseModel):
    is_correct: bool
    reason: str


def is_answer_correct(question: str, suggested_answer: str) -> IsAnswerCorrect:
    user_content = f"<question>{question}</question>\n<suggested_answer>{suggested_answer}</suggested_answer>"
    messages = [
        {"role": Role.SYSTEM, "content": constants.SYSTEM_PROMPT_EVALUATE},
        {
            "role": Role.USER,
            "content": user_content,
        },
    ]

    completion = openai.beta.chat.completions.parse(
        model=os.environ.get("OPENAI_MODEL"),
        messages=messages,
        response_format=IsAnswerCorrect,
        temperature=0.2,
        top_p=0.2,
    )
    parsed_obj = completion.choices[0].message.parsed
    return parsed_obj


def get_assert(output, context) -> Union[bool, float, Dict[str, Any]]:
    print(f"context: {context}")
    enable_test = context["vars"]["enable_test"]
    score, is_pass = 0, False
    if enable_test.upper() == "FALSE":
        return {
            "pass": True,
            "score": 1,
            "reason": "Test case is disabled. Set 'enable_test' to 'True' to enable it.",
        }

    generated_question = output["generated_question"]
    generated_answer = output["generated_answer"]
    # llm-as-judge
    is_answer_correct_obj = is_answer_correct(
        question=generated_question, suggested_answer=generated_answer
    )
    if is_answer_correct_obj.is_correct:
        is_pass = True
        score += 1
    print(f"is_answer_correct_obj: {is_answer_correct_obj}")
    print(f"Current Working Directory: {os.getcwd()}")
    return {
        "pass": is_pass,
        "score": score,
        "reason": is_answer_correct_obj.reason,
    }
