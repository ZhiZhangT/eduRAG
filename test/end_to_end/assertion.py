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

load_dotenv()


class RelevanceScoreResponse(BaseModel):
    score: int
    reason: str


def get_relevance_score(
    llm_response: str, similar_documents: str
) -> RelevanceScoreResponse:
    messages = [
        {"role": "system", "content": constants.SYSTEM_PROMPT_EVALUATE},
        {
            "role": "user",
            "content": f"'llm_response': {llm_response} 'similar_documents': {similar_documents}",
        },
    ]

    completion = openai.beta.chat.completions.parse(
        # NOTE: hardcode the model for now as this is the only gpt4o model that supports structured outputs
        # see here for more information: https://platform.openai.com/docs/guides/structured-outputs/introduction
        model=os.environ.get("OPENAI_MODEL"),
        messages=messages,
        response_format=RelevanceScoreResponse,
        temperature=0.2,
        top_p=0.2,
    )
    parsed_obj = completion.choices[0].message.parsed
    return parsed_obj


def get_assert(output, context) -> Union[bool, float, Dict[str, Any]]:
    print(f"context: {context}")
    enable_test = context["vars"]["enable_test"]
    if enable_test.upper() == "FALSE":
        return {
            "pass": True,
            "score": 1,
            "reason": "Test case is disabled. Set 'enable_test' to 'True' to enable it.",
        }

    response = output["response"]
    similar_documents = output["similar_documents"]
    relevance_score_obj = get_relevance_score(response, similar_documents)
    print(f"Relevance score object: {relevance_score_obj}")
    if relevance_score_obj.score < 0.5:
        return {
            "pass": False,
            "score": relevance_score_obj.score,
            "reason": relevance_score_obj.reason,
        }

    return {
        "pass": True,
        "score": relevance_score_obj.score,
        "reason": relevance_score_obj.reason,
    }
