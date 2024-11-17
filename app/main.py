import os
import openai
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from datetime import datetime, timezone
from app.models import QuestionData
from app.utils.format_utils import convert_exam_type, normalise_query
from app.utils.openai_utils import get_embedding
from app.db.vector_search import vector_search
from app.utils.openai_utils import get_llm_response
from app.models import Message

load_dotenv()

# initialise FastAPI app
app = FastAPI()

openai.api_key = os.environ.get("OPENAI_API_KEY")

# connect to MongoDB
mongo_client = MongoClient(os.environ.get("MONGODB_URI"))
db = mongo_client["exam_db"]
question_collection = db["question"]


# endpoint to accept JSON data and store in MongoDB
@app.post("/upload-questions")
def upload_questions(request_obj: QuestionData):
    try:
        meta_info = request_obj.meta_info.model_dump()

        # convert exam_type to enum value
        exam_type = convert_exam_type(meta_info.get("exam_type", ""))

        # iterate over each question and insert into MongoDB
        for idx, question_item in enumerate(request_obj.questions, start=1):
            # clean question data
            question_body = question_item.question.strip()
            category = question_item.category.strip()
            question_type = question_item.question_type.strip()
            question_number = int(question_item.question_number.strip())
            question_part = question_item.question_part.strip()

            # get embedding for question body
            question_body_embedding = get_embedding(question_body)

            # prepare document to insert
            question_document = {
                "page_start": question_item.page_start,
                "page_end": question_item.page_end,
                "question_number": question_number,
                "question_part": question_part,
                "question_body": question_body,
                "question_body_embedding": question_body_embedding,
                "topic": category,
                "sub_topic": question_type,
                "answer_body": "",
                "question_paper_filepath": request_obj.question_paper_filepath.strip(),
                "answer_paper_filepath": "",  # TODO: Add answer paper filepath
                "subject": meta_info.get("subject", ""),
                "paper_number": meta_info.get("paper", ""),
                "level": meta_info.get("level", ""),
                "exam_type": exam_type,
                "school": meta_info.get("school", ""),
                "created_utc": datetime.now(timezone.utc),
                "updated_utc": datetime.now(timezone.utc),
            }

            # insert document into MongoDB
            question_collection.insert_one(question_document)

        return JSONResponse(
            status_code=200, content={"message": "Exam data uploaded successfully."}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# endpoint to ask a question
@app.post("/query")
def query(user_query: list[Message]):
    try:
        user_query = normalise_query(user_query)
        results = vector_search(user_query[-1].content, question_collection)
        user_query[-1].content += f"""\n\nSIMILAR_DOCUMENTS: {results}"""
        response = get_llm_response(user_query)
        return JSONResponse(status_code=200, content={"response": response})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
