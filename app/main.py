import os
import openai
import json
import types
import sys
import traceback
from typing import Optional, Any
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from datetime import datetime, timezone
from app.models import QuestionData
from app.utils.format_utils import (
    convert_exam_type,
    normalise_query,
    format_first_question_xml,
    format_generated_answer,
)
from app.utils.openai_utils import get_embedding
from app.db.vector_search import vector_search
from app.utils.openai_utils import (
    get_generated_questions_and_answers,
    get_python_script_and_answer,
    get_corrected_python_script,
    get_format_matched_script,
)
from app.models import Message
from app.utils.image_utils import extract_question_metadata, find_and_crop_image
from app import constants
from ulid import ULID

load_dotenv()

# initialise FastAPI app
app = FastAPI()

openai.api_key = os.environ.get("OPENAI_API_KEY")

# connect to MongoDB
MONGODB_URI = os.environ.get("MONGODB_URI")
print(f"Connecting to MongoDB at {MONGODB_URI}")
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client["exam_db"]
question_collection = db["question"]


# endpoint to accept JSON data and store in MongoDB
@app.post("/upload-questions")
def upload_questions(request_obj: QuestionData):
    try:
        meta_info = request_obj.meta_info.model_dump()
        exam_type = convert_exam_type(meta_info.get("exam_type", ""))
        update_count, insert_count = 0, 0

        for question_item in request_obj.questions:
            # clean question data
            question_body = question_item.question.strip()
            category = question_item.category.strip()
            question_type = question_item.question_type.strip()
            question_number = int(question_item.question_number.strip())
            question_part = question_item.question_part.strip()
            answer_paper_filepath = (
                ""
                if not request_obj.answer_paper_filepath
                else request_obj.answer_paper_filepath.strip()
            )

            # check if question exists
            existing_question = question_collection.find_one(
                {"question_body": question_body}
            )

            if existing_question:
                # update existing document
                update_document = {
                    "page_start": question_item.page_start,
                    "page_end": question_item.page_end,
                    "question_number": question_number,
                    "question_part": question_part,
                    "topic": category,
                    "sub_topic": question_type,
                    "answer_body": "",
                    "question_paper_filepath": request_obj.question_paper_filepath.strip(),
                    "answer_paper_filepath": answer_paper_filepath,
                    "subject": meta_info.get("subject", ""),
                    "paper_number": meta_info.get("paper", ""),
                    "level": meta_info.get("level", ""),
                    "exam_type": exam_type,
                    "year": int(meta_info.get("year", -1)),
                    "school": meta_info.get("school", ""),
                    "updated_utc": datetime.now(timezone.utc),
                }

                question_collection.update_one(
                    {"question_body": question_body}, {"$set": update_document}
                )
                print(f"[INFO] Updated question: {question_body}")
                update_count += 1
            else:
                # get embedding for new question
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
                    "answer_paper_filepath": answer_paper_filepath,
                    "subject": meta_info.get("subject", ""),
                    "paper_number": meta_info.get("paper", ""),
                    "level": meta_info.get("level", ""),
                    "exam_type": exam_type,
                    "year": int(meta_info.get("year", -1)),
                    "school": meta_info.get("school", ""),
                    "created_utc": datetime.now(timezone.utc),
                    "updated_utc": datetime.now(timezone.utc),
                }

                question_collection.insert_one(question_document)
                insert_count += 1
                print(f"[INFO] Inserted question: {question_body}")
        print(
            f"[INFO] Inserted {insert_count} new questions and updated {update_count} existing questions."
        )

        return JSONResponse(
            status_code=200, content={"message": "Exam data uploaded successfully."}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# endpoint to ask a question
@app.post("/query")
def query(
    user_query: list[Message],
    subject: Optional[str] = Body(default="elementary_mathematics"),
    level: Optional[str] = Body(default=None),
    exam_type: Optional[str] = Body(default=None),
):
    try:
        user_query = normalise_query(user_query)
        results = vector_search(
            user_query[-1].content, question_collection, [subject, level, exam_type]
        )
        if not results:
            raise HTTPException(
                status_code=404,
                detail="No similar questions found. Please try again with a different question.",
            )
        # find the question text in the question paper PDF and crop out an image containing the question
        question_paper_filepath, question_body, image_filename, page_start, page_end = (
            extract_question_metadata(results[0])
        )
        find_and_crop_image(
            pdf_url=question_paper_filepath,
            search_text=question_body,
            question_filename=image_filename,
            page_start=page_start,
            page_end=page_end,
        )
        image_filepath = f"{constants.TEMP_DIR}/{image_filename}.png"
        first_question_xml = format_first_question_xml(results)
        # pass the question metadata (topic, subtopic, link) + question image to OpenAI
        # NOTE: the question image was used instead of the question_body field because the question_body field is generally inaccurate
        response = get_generated_questions_and_answers(
            question_details=first_question_xml, image_filepath=image_filepath
        )
        # ensure that the output directory exists
        os.makedirs(constants.OUTPUT_DIR, exist_ok=True)
        # store the generated questions and answers into a JSON file
        json_filepath = f"{constants.OUTPUT_DIR}/{image_filename}_{str(ULID())}.json"
        response_dict = response.model_dump()
        response_dict["ground_truth"] = {
            "topic": results[0]["topic"],
            "sub_topic": results[0]["sub_topic"],
            "question_part": results[0]["question_part"],
            "subject": results[0]["subject"],
            "paper_number": results[0]["paper_number"],
            "level": results[0]["level"],
            "exam_type": results[0]["exam_type"],
            "year": results[0]["year"],
            "school": results[0]["school"],
            "question_url": f"{results[0]['question_paper_filepath']}#page={results[0]['page_start']}",
        }
        with open(json_filepath, "w") as f:
            json.dump(response_dict, f, indent=4)

        return {"response": response_dict, "first_question": first_question_xml}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/verify")
def verify():
    responses = []

    # Iterate through JSON files in output directory
    for filename in os.listdir(constants.OUTPUT_DIR):
        if not filename.endswith(".json"):
            continue

        filename_without_extension = os.path.splitext(filename)[0]

        skip_file = False
        # if there already exists a python file that contains filename_without_extension, skip this file
        for f in os.listdir(constants.OUTPUT_DIR):
            if f.endswith(".py") and filename_without_extension in f:
                skip_file = True
                break
        if skip_file:
            continue

        json_path = os.path.join(constants.OUTPUT_DIR, filename)

        # Read JSON file
        with open(json_path) as f:
            data = json.load(f)

        # Iterate through questions
        for i, question_doc in enumerate(data.get("questions", [])):
            num_tries = 0
            last_script = None
            last_error = None
            last_computed_answer = None
            suggested_answer = format_generated_answer(question_doc["answer"])

            # try to generate and run the python script up to 6 times
            while num_tries < 6:
                try:
                    # Generate python script and get answer
                    if last_script is None and last_computed_answer is None:
                        # First attempt - generate new script
                        response = get_python_script_and_answer(
                            question_text=question_doc["question_text"],
                            suggested_answer=suggested_answer,
                        )
                    elif last_script is not None and last_computed_answer is None:
                        # Attempt to correct Python script for syntax errors
                        print(f"Attempting to correct Python script...")
                        response = get_corrected_python_script(
                            question_text=question_doc["question_text"],
                            suggested_answer=suggested_answer,
                            previous_script=last_script,
                            error_message=last_error,
                        )
                        print(f"response: {response}")
                    else:
                        # Attempt to match output format
                        print(f"Attempting to match output format...")
                        response = get_format_matched_script(
                            question_text=question_doc["question_text"],
                            suggested_answer=suggested_answer,
                            previous_script=last_script,
                            computed_answer=last_computed_answer,
                        )

                    # Save python script to file
                    script_filename = (
                        f"{constants.OUTPUT_DIR}/{filename_without_extension}_{i}.py"
                    )
                    with open(script_filename, "w") as f:
                        f.write(response.python_script)

                    # Run the script
                    computed_answer = _run_dynamic_code(response.python_script)

                    is_exact_match = computed_answer == suggested_answer

                    # Add to responses
                    responses.append(
                        {
                            "filename": filename,
                            "attempt": num_tries + 1,
                            "question_index": i,
                            "response": response,
                            "suggested_answer": suggested_answer,
                            "computed_answer": computed_answer,
                            "is_exact_match": is_exact_match,
                        }
                    )

                    # if the code runs successfully and there is an exact match, break out of the loop
                    if is_exact_match:
                        break
                    else:
                        # store the script and computed answer so that we can try correcting the format of the computed answer
                        last_script = response.python_script
                        last_computed_answer = computed_answer

                except HTTPException:
                    raise
                except Exception as e:
                    # Store the script and error for next iteration
                    last_script = (
                        response.python_script if "response" in locals() else None
                    )
                    last_error = str(e)
                    # prints the full error trace
                    print(traceback.format_exc())
                    print(
                        f"[INFO] Attempt {num_tries + 1} failed for {filename} question {i}"
                    )
                finally:
                    num_tries += 1

    return responses


# runs python code in memory
def _run_dynamic_code(code_string: str) -> Any:
    module_name = "dynamic_solution"
    # Creates a module object directly in memory
    module = types.ModuleType("dynamic_solution")

    # Registers module in sys.modules (Python's module cache)
    sys.modules[module_name] = module

    try:
        # Executes code directly in the module's namespace
        exec(code_string, module.__dict__)
        return module.solve_problem()
    finally:
        # Only needs to clean up the module reference
        del sys.modules[module_name]
