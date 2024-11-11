import os
import time
import openai
from pymongo import MongoClient, UpdateOne
from typing import List
from dotenv import load_dotenv


def get_embedding(text: str, model="text-embedding-3-small") -> List[float]:
    """Get embedding for a given text using OpenAI's API"""
    try:

        response = openai.embeddings.create(input=text, model=model)
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return None


def process_documents(mongo_client: MongoClient, batch_size: int = 20):
    """Process documents in batches"""
    db = mongo_client["exam_db"]
    collection = db["question"]
    # find documents without embeddings
    query = {"question_body_embedding": {"$exists": False}}
    documents = collection.find(query)

    updates = []
    count = 0

    for doc in documents:
        if "question_body" not in doc:
            continue

        # get embedding for question body
        embedding = get_embedding(doc["question_body"])

        if embedding:
            update_operation = UpdateOne(
                {"_id": doc["_id"]}, {"$set": {"question_body_embedding": embedding}}
            )
            updates.append(update_operation)
            count += 1

        # process in batches to avoid memory issues
        if len(updates) >= batch_size:
            try:
                collection.bulk_write(updates)
                print(f"Processed {count} documents")
                updates = []
            except Exception as e:
                print(f"Error in bulk write: {e}")

            # sleep to avoid rate limits
            time.sleep(1)

    # process remaining updates
    if updates:
        try:
            collection.bulk_write(updates)
            print(f"Processed final batch. Total documents processed: {count}")
        except Exception as e:
            print(f"Error in final bulk write: {e}")


if __name__ == "__main__":
    load_dotenv()
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    mongo_client = MongoClient(os.environ.get("MONGODB_URI"))

    process_documents(mongo_client)
