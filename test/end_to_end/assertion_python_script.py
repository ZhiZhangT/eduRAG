import os
import sys
from typing import Dict, Union, Any
from dotenv import load_dotenv

# Get the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory of the current directory
parent_dir = os.path.dirname(current_dir)
# Get the parent directory of the parent directory (which should contain 'app')
grandparent_dir = os.path.dirname(parent_dir)
# Add the grandparent directory to sys.path
sys.path.append(grandparent_dir)
from app.main import verify

load_dotenv()


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

    provider_response = context["providerResponse"]
    json_filepath = provider_response["json_filepath"]
    # exact match using generated python script
    verify_response = verify(json_filepath=json_filepath)
    last_response = verify_response[-1]
    suggested_answer = last_response["suggested_answer"]
    computed_answer = last_response["computed_answer"]
    is_last_response_correct = last_response["is_exact_match"]
    if is_last_response_correct:
        is_pass = True
        score += 1
    return {
        "pass": is_pass,
        "score": score,
        "reason": f"Suggested answer: {suggested_answer}, Computed answer: {computed_answer}",
    }
