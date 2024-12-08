import os
import sys
import openai
from typing import Dict, Union, Any, List
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


class StepValidation(BaseModel):
    step_number: int
    is_valid: bool
    explanation: str


class StepByStepResponse(BaseModel):
    question_type: str
    is_correct: bool
    step_validations: List[StepValidation]
    conclusion: str


def is_answer_correct_step_by_step(
    question: str, suggested_answer: str, steps: List[str]
) -> StepByStepResponse:
    user_content = f"<question>{question}</question>"
    for i, step in enumerate(steps):
        user_content += f"\n<step_{i}>{step}</step_{i}>"
    user_content += f"\n<suggested_answer>{suggested_answer}</suggested_answer>"
    messages = [
        {"role": Role.SYSTEM, "content": constants.SYSTEM_PROMPT_EVALUATE_STEP_BY_STEP},
        {
            "role": Role.USER,
            "content": user_content,
        },
    ]

    completion = openai.beta.chat.completions.parse(
        model=os.environ.get("OPENAI_MODEL"),
        messages=messages,
        response_format=StepByStepResponse,
        temperature=0.2,
        top_p=0.2,
    )
    parsed_obj = completion.choices[0].message.parsed
    return parsed_obj


def get_assert(output, context) -> Union[bool, float, Dict[str, Any]]:
    provider_response = context["providerResponse"]
    enable_test = context["vars"]["enable_test"]
    score, is_pass = 0, False
    if enable_test.upper() == "FALSE":
        return {
            "pass": True,
            "score": 1,
            "reason": "Test case is disabled. Set 'enable_test' to 'True' to enable it.",
        }

    steps = provider_response["steps"]
    generated_question = output["generated_question"]
    generated_answer = output["generated_answer"]
    # llm-as-judge-step-by-step
    is_answer_correct_obj = is_answer_correct_step_by_step(
        question=generated_question, suggested_answer=generated_answer, steps=steps
    )
    reason = is_answer_correct_obj.conclusion
    if is_answer_correct_obj.is_correct:
        is_pass = True
        score += 1
    else:
        for step_validation in is_answer_correct_obj.step_validations:
            if not step_validation.is_valid:
                reason += f"\nStep {step_validation.step_number}: {step_validation.explanation}"
    return {
        "pass": is_pass,
        "score": score,
        "reason": reason,
    }
