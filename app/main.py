import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from datetime import datetime, timezone
from app.models import QuestionData
from app.utils.format_utils import clean_meta_info, convert_exam_type

load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Connect to MongoDB
client = MongoClient(os.environ.get("MONGODB_URI"))
db = client["exam_db"]
question_collection = db["question"]


# Endpoint to accept JSON data and store in MongoDB
@app.post("/upload_questions")
async def upload_questions(questions: QuestionData):
    try:
        # Clean meta_info
        meta_info_dict = questions.meta_info.model_dump()
        cleaned_meta_info = clean_meta_info(meta_info_dict)

        # Convert exam_type to enum value
        exam_type = convert_exam_type(cleaned_meta_info.get("exam_type", ""))

        # Iterate over each question and insert into MongoDB
        for idx, question_item in enumerate(questions.questions, start=1):
            # Clean question data
            question_body = question_item.question.strip()
            category = question_item.category.strip()
            question_type = question_item.question_type.strip()

            # Prepare document to insert
            question_document = {
                "page_start": question_item.page_start,
                "page_end": question_item.page_end,
                "question_number": idx,  # Assuming sequential numbering; TODO: add in question and sub-question
                "question_body": question_body,
                "topic": category,
                "sub_topic": question_type,
                "answer_body": "",
                "question_filepath": questions.question_filepath.strip(),
                "question_filename": questions.question_filename.strip(),
                "answer_filepath": "",
                "answer_filename": "",
                "subject": cleaned_meta_info.get("subject", ""),
                "paper_number": cleaned_meta_info.get("paper", ""),
                "level": questions.level.strip(),  # TODO: use AI to determine level
                "exam_type": exam_type,
                "school": cleaned_meta_info.get("school", ""),
                "created_utc": datetime.now(timezone.utc),
                "updated_utc": datetime.now(timezone.utc),
            }

            # Insert document into MongoDB
            question_collection.insert_one(question_document)

        return JSONResponse(
            status_code=200, content={"message": "Exam data uploaded successfully."}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
