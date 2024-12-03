import os
from typing import Optional
import openai
from pydantic import BaseModel
from pymongo.collection import Collection

# UNCOMMENT below to run the file from the main.py file
from app.utils.openai_utils import get_embedding
from app.constants import SUBJECT_MAPPING
from app.models import AMathTopicEnum, EMathTopicEnum
from app.utils.retrieveal_eval_utils import evaluate_retrieval

# UNCOMMENT below to run the file directly
# from app.constants import SUBJECT_MAPPING
# from app.utils.openai_utils import get_embedding
# from app.utils.retrieveal_eval_utils import evaluate_retrieval

from dotenv import load_dotenv
from pymongo import MongoClient

import json


def vector_search(user_query: str, collection: Collection, query_variables: list = ["additional_mathematics", None, None]) -> list:
    """
    Perform a vector search in the MongoDB collection based on the user query.

    Args:
    user_query (str): The user's query string.
    collection (MongoCollection): The MongoDB collection to search.
    query_variables (list): The list of query variables to consider: [subject, level, exam_type].

    Returns:
    list: A list of matching documents.
    """
    
    subject, level, exam_type = query_variables
    
    # Set your OpenAI API key
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get("OPENAI_MODEL")
    
    client = openai.OpenAI()
    
    topics = SUBJECT_MAPPING.get(subject, {})
    # print(topics)
    
    class Topic(BaseModel):
        if subject == "elementary_mathematics":
            topic: Optional[EMathTopicEnum]
        else:
            topic: Optional[AMathTopicEnum]
    
    topic_completion = client.beta.chat.completions.parse(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "The user query is from a student who is preparing for a math exam. Determine the topic type that the user is asking about. If there are no relevant topics, return null."},
            {"role": "user", "content": user_query}
        ],
        response_format=Topic,
        )

    topic = topic_completion.choices[0].message.parsed.model_dump()['topic'].value
    # print(f"topic: {topic}")
    
    class SubTopic(BaseModel):
        sub_topic: str
    
    sub_topic_completion = client.beta.chat.completions.parse(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "The user query is from a student who is preparing for a math exam. Determine one sub-topic from the list of possible sub-topics that is most relevant to the user query. If there are no relevant sub-topics, return null."},
            {"role": "user", "content": "The list of sub-topics are: " + str(topics[topic]) + "/n The user query is: " + user_query}
        ],
        response_format=SubTopic,
        )
    
    sub_topic = sub_topic_completion.choices[0].message.parsed.model_dump()['sub_topic']
    # print(f"sub_topic: {sub_topic}")
    
    # Define the MQL query:
    mql = {
    "$and": [
        {"subject": {"$eq": subject} if subject else {"$exists": True}},
        {"topic": {"$eq": topic} if topic else {"$ne": "None"}},
        {"sub_topic": {"$eq": sub_topic} if sub_topic else {"$ne": "None"}},
        {"level": {"$eq": level} if level else {"$ne": "None"}},
        {"exam_type": {"$eq": exam_type} if exam_type else {"$ne": "None"}},
        ]
    }

    
    print(f"mql: {mql}")
    
    # mql = {'$and': [{'subject': 'elementary_mathematics'}, {'topic': 'Pythagoras’ theorem and trigonometry'}, {'sub_topic': {'$exists': True}}, {'level': {'$exists': True}}, {'exam_type': {'$exists': True}}]}
    
    # Generate embedding for the user query
    query_embedding = get_embedding(user_query)

    if query_embedding is None:
        return "Invalid query or embedding generation failed."

    # Define the vector search pipeline
    pipeline = [
        {
            "$vectorSearch": {
                "index": "question_body_vector_index",
                "queryVector": query_embedding,
                "path": "question_body_embedding",
                "numCandidates": 50,  # Number of candidate matches to consider
                "limit": 3,  # Number of final matches to return
                "filter": mql,  # Filter based on the MQL query
            }
        },
        # TODO: implement some form of empirical threshold based on vector score?
        {
            "$project": {
                # "_id": 0,  # Exclude the _id field
                "question_body_embedding": 0,  # Exclude the question_body_embedding field
                "score": {"$meta": "vectorSearchScore"},  # Include the search score
            }
        },
    ]

    # Execute the search
    results = collection.aggregate(pipeline)
    return list(results)


if __name__ == "__main__":
    load_dotenv()
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    mongo_client = MongoClient(os.environ.get("MONGODB_URI"))
    db = mongo_client["exam_db"]
    collection = db["question"]
    user_query = "Could you provide me with practice problems on applications of the binomial theorem?"
    ground_truth_docIDs = "'674dcd3ab00b977d048c92e0'; '674dcd15b00b977d048c92b7'; '674dcd15b00b977d048c92b8'; '674dcd16b00b977d048c92b9'; '674dcd3bb00b977d048c92e2'"
    ground_truth = [docID.strip() for docID in ground_truth_docIDs.split(";")]

    results = vector_search(user_query, collection)
    
    ground_truth_docIDs = "'674dcd3ab00b977d048c92e0'; '674dcd15b00b977d048c92b7'; '674dcd15b00b977d048c92b8'; '674dcd16b00b977d048c92b9'; '674dcd3bb00b977d048c92e2'"
    ground_truth = [docID.strip()[1:-1] for docID in ground_truth_docIDs.split(";")]
    results = [str(result["_id"]) for result in results]
    
    print(f"ground_truth: {ground_truth}")
    print("\n\n")
    print(f"results: {results}")
    
    evaluate_retrieval(ground_truth, results)
    results_dict = evaluate_retrieval(ground_truth, results)
    print(f"results_dict: {results_dict}")
