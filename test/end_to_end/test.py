import sys
import os
import json

# Get the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory of the current directory
parent_dir = os.path.dirname(current_dir)
# Get the parent directory of the parent directory (which should contain 'app')
grandparent_dir = os.path.dirname(parent_dir)
# Add the grandparent directory to sys.path
sys.path.append(grandparent_dir)

from app.main import query
from app.models import Message, Role


def call_api(prompt, options, context):
    enable_test = context["vars"]["enable_test"]
    if enable_test.upper() == "FALSE":
        return {
            "output": {
                "response": "Test case is disabled. Set 'enable_test' to 'True' to enable it.",
            },
        }
    try:
        user_query = context["vars"]["query"]
        messages = [Message(content=user_query, role=Role.USER)]

        response = query(messages)
        response_body = json.loads(response.body)

        result = {
            "output": {
                "response": response_body["response"],
                "similar_documents": response_body["similar_documents"],
            }
        }

        return result
    except Exception as e:
        raise e
