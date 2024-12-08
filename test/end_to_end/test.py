import sys
import os
from pylatexenc.latex2text import LatexNodes2Text

# Get the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory of the current directory
parent_dir = os.path.dirname(current_dir)
# Get the parent directory of the parent directory (which should contain 'app')
grandparent_dir = os.path.dirname(parent_dir)
# Add the grandparent directory to sys.path
sys.path.append(grandparent_dir)

from app.main import query
from app.models import Message, Role, QueryRequest


def call_api(prompt, options, context):
    enable_test = context["vars"]["enable_test"]
    is_plain_text = context["vars"]["is_plain_text"].upper() == "TRUE"
    remove_latex = context["vars"]["remove_latex"].upper() == "TRUE"
    if enable_test.upper() == "FALSE":
        return {
            "output": {
                "response": "Test case is disabled. Set 'enable_test' to 'True' to enable it.",
            },
        }
    try:
        user_query = context["vars"]["query"]
        subject = context["vars"]["subject"]
        messages = [Message(content=user_query, role=Role.USER)]

        query_request = QueryRequest(
            user_query=messages, subject=subject, is_plain_text=is_plain_text
        )

        res = query(request=query_request)
        response = res["response"]
        json_filepath = res["json_filepath"]

        answer = response["answer"]

        if remove_latex:
            answer = LatexNodes2Text().latex_to_text(answer)

        result = {
            "output": {
                "query_id": response["query_id"],
                "generated_question": response["question_text"],
                "generated_answer": response["answer"],
            },
            "json_filepath": json_filepath,
            "steps": response["steps"],
        }

        return result
    except Exception as e:
        raise e
