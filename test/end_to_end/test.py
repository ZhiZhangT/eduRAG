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
from app.models import Message, Role, QueryRequest


def call_api(prompt, options, context):
    enable_test = context["vars"]["enable_test"]
    is_plain_text = context["vars"]["is_plain_text"].upper() == "TRUE"
    use_image = context["vars"]["use_image"].upper() == "TRUE"
    use_few_shot = context["vars"]["use_few_shot"].upper() == "TRUE"
    retrieved_docs_count = int(context["vars"]["retrieved_docs_count"])
    if enable_test.upper() == "FALSE":
        return {
            "output": {
                "response": "Test case is disabled. Set 'enable_test' to 'True' to enable it.",
            },
        }
    try:
        user_query = context["vars"]["query"]
        subject = context["vars"]["subject"]
        sub_topic = context["vars"]["sub_topic"]
        # load retrieved documents from "retrieved_docs_for_sub_topic.json"
        with open("test/end_to_end/retrieved_docs_for_sub_topic.json", "r") as f:
            retrieved_documents_for_sub_topic = json.load(f)
        retrieved_documents = retrieved_documents_for_sub_topic[sub_topic]
        retrieved_documents = retrieved_documents[:retrieved_docs_count]
        print(
            f"retrieved_docs_count: {retrieved_docs_count} num_retrieved_docs: {len(retrieved_documents)}"
        )
        messages = [Message(content=user_query, role=Role.USER)]

        query_request = QueryRequest(
            user_query=messages,
            subject=subject,
            is_plain_text=is_plain_text,
            retrieved_documents=retrieved_documents,
            use_image=use_image,
            use_few_shot=use_few_shot,
        )

        res = query(request=query_request)
        response = res["response"]
        json_filepath = res["json_filepath"]

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
