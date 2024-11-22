import os
import openai
from pymongo.collection import Collection

# UNCOMMENT below to run the file from the main.py file
from app.utils.openai_utils import get_embedding
from app.constants import SUBJECT_MAPPING

# UNCOMMENT below to run the file directly
# from utils.openai_utils import get_embedding
# from constants import SUBJECT_MAPPING

from dotenv import load_dotenv
from pymongo import MongoClient


from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import json

# Set your OpenAI API key
openai.api_key = os.environ.get('OPENAI_API_KEY')

llm = ChatOpenAI(temperature=0, model_name='gpt-4o', api_key=openai.api_key)

def vector_search(user_query: str, collection: Collection, query_variables: list = ["elementary_mathematics", "All", "All"]) -> list:
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
    
    # Generate MongoDB Query Language (MQL) based on the user query
    text_to_mql_query_prompt_template = """
        Convert the following user query to MongoDB Query Language (MQL).

        User Query: "{user_query}"

        Only focus on the following fields in the collection:
        - "topic", e.g., "Surds"
        - "sub_topic", e.g., "Rationalising denominator of surd"

        You should refer to a list of valid topics and sub_topics from this JSON object:
        {topics_json}

        Note that the chosen sub_topic must be nested within the chosen topic.

        The MQL query should return documents that match the user query based on the "topic" and "sub_topic" fields.
        Return the MQL query as a JSON object only, without anything else. e.g.:

        {{
            "$and": [
                {{"topic": "Surds"}},
                {{"sub_topic": "Rationalising denominator of surd"}}
            ]
        }}
    """

    
    topics_json = SUBJECT_MAPPING.get(subject, {})
    # print(topics_json)
    
    text_to_mql_query_prompt = PromptTemplate(
        template=text_to_mql_query_prompt_template,
        input_variables=["user_query", "topics_json"]
    )
    '''
    text_to_mql_chain = LLMChain(llm=llm, prompt=text_to_mql_query_prompt)
    mql_response = text_to_mql_chain.run(
        user_query=user_query,
        topics_json=json.dumps(topics_json)
    )
    print(mql_response)
    mql = json.loads(mql_response.strip('```json').strip('```').strip())
    print(mql)
    '''
    mql = {'$and': [{'topic': 'Problems in real-world contexts'}, {'sub_topic': 'Calculating the percentage profit'}]}
    
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
                "_id": 0,  # Exclude the _id field
                "question_body_embedding": 0,  # Exclude the question_body_embedding field
                "score": {"$meta": "vectorSearchScore"},  # Include the search score
            }
        },
    ]
    
    query_plan = collection.aggregate(pipeline).explain()
    print(query_plan)

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
