import os
from typing import Optional
import openai
from pydantic import BaseModel
from pymongo.collection import Collection
from dotenv import load_dotenv
from pymongo import MongoClient

# UNCOMMENT below to run the file from the main.py file
from app.utils.openai_utils import get_embedding
from app.constants import SUBJECT_MAPPING
from app.models import AMathTopicEnum, EMathTopicEnum
from app.utils.retrieveal_eval_utils import evaluate_retrieval

# UNCOMMENT below to run the file directly
# from app.constants import SUBJECT_MAPPING
# from app.utils.openai_utils import get_embedding
# from app.utils.retrieveal_eval_utils import evaluate_retrieval

import json
import cachetools

# Set your OpenAI API key
openai.api_key = os.environ.get('OPENAI_API_KEY')
OPENAI_MODEL = os.environ.get("OPENAI_MODEL")

client = openai.OpenAI()

topics_cache = cachetools.LRUCache(maxsize=100)
subtopics_cache = cachetools.LRUCache(maxsize=100)

def get_topic_from_openai(user_query: str, format):
    if user_query in topics_cache:
        return topics_cache[user_query]
    else:
        print("Sending request to OpenAI API to get topic...")
        topic_completion = client.beta.chat.completions.parse(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "The user query is from a student who is preparing for a math exam. Determine the topic type that the user is asking about. If there are no relevant topics, return null."},
                {"role": "user", "content": user_query}
            ],
            response_format=format,
            )
        topic = topic_completion.choices[0].message.parsed.model_dump()['topic'].value
        topics_cache[user_query] = topic
        
        return topic

def get_sub_topic_from_openai(user_query: str, topics_json: str, topic: str, format):
    if (user_query, topic) in subtopics_cache:
        return subtopics_cache[(user_query, topic)]
    else:
    
        print("Sending request to OpenAI API to get sub-topic...")
        # Convert topics_json back to a dictionary
        topics = json.loads(topics_json)
        
        sub_topic_completion = client.beta.chat.completions.parse(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "The user query is from a student who is preparing for a math exam. Determine one sub-topic from the list of possible sub-topics that is most relevant to the user query. If there are no relevant sub-topics, return null."},
                {"role": "user", "content": "The list of sub-topics are: " + str(topics[topic]) + "/n The user query is: " + user_query}
            ],
            response_format=format,
        )
        
        sub_topic = sub_topic_completion.choices[0].message.parsed.model_dump()['sub_topic']
        subtopics_cache[(user_query, topic)] = sub_topic
        
        return sub_topic

def vector_search(user_query: str, collection: Collection, query_variables: list = ["additional_mathematics", None, None], numCandidates: int = 50, returnLimit: int = 3, mql: bool = False) -> list:
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
    if mql:
        topics = SUBJECT_MAPPING.get(subject, {})
        # print(topics)
        
        class Topic(BaseModel):
            if subject == "elementary_mathematics":
                topic: Optional[EMathTopicEnum]
            else:
                topic: Optional[AMathTopicEnum]
        
        
        topic = get_topic_from_openai(user_query, format=Topic)
        # print(f"topic: {topic}")
        
        class SubTopic(BaseModel):
            sub_topic: str
        
        sub_topic = get_sub_topic_from_openai(user_query, json.dumps(topics), topic, format=SubTopic)
        # print(f"sub_topic: {sub_topic}")
    else:
        topic = None
        sub_topic = None
        
    # Define the MQL query:
    mql_query = {
    "$and": [
        {"subject": {"$eq": subject} if subject else {"$exists": True}},
        {"topic": {"$eq": topic} if topic else {"$ne": "None"}},
        {"sub_topic": {"$eq": sub_topic} if sub_topic else {"$ne": "None"}},
        {"level": {"$eq": level} if level else {"$ne": "None"}},
        {"exam_type": {"$eq": exam_type} if exam_type else {"$ne": "None"}},
        ]
    }

    
    # print(f"mql: {mql_query}")
    
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
                "numCandidates": numCandidates,  # Number of candidate matches to consider
                "limit": returnLimit,  # Number of final matches to return
                "filter": mql_query,  # Filter based on the MQL query
            } if mql else 
            {
                "$vectorSearch": {
                    "index": "question_body_vector_index",
                    "queryVector": query_embedding,
                    "path": "question_body_embedding",
                    "numCandidates": numCandidates,  # Number of candidate matches to consider
                    "limit": returnLimit,  # Number of final matches to return
                }
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
