import os
import openai
from pymongo.collection import Collection

# UNCOMMENT below to run the file from the main.py file
from app.create_vector_embeddings import get_embedding

# UNCOMMENT below to run the file directly
# from create_vector_embeddings import get_embedding
from dotenv import load_dotenv
from pymongo import MongoClient


def vector_search(user_query: str, collection: Collection) -> list:
    """
    Perform a vector search in the MongoDB collection based on the user query.

    Args:
    user_query (str): The user's query string.
    collection (MongoCollection): The MongoDB collection to search.

    Returns:
    list: A list of matching documents.
    """

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
            }
        },
        # TODO: implement some form of empirical threshold based on vector score?
        {
            "$project": {
                "_id": 0,  # Exclude the _id field
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
    user_query = "Where can I find the question related to a warehouse sale?"

    results = vector_search(user_query, collection)
    print(f"results: {results}")
