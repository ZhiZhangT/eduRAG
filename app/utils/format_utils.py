import re
from app.models import Message


def convert_exam_type(exam_type):
    # Map exam type to enum values
    exam_type_mapping = {
        "preliminary examination": "prelim",
        "mid year examination": "mid_year",
        "final year examination": "final_year",
        "test": "test",
    }
    return exam_type_mapping.get(exam_type, exam_type)


def normalise_query(query: list[Message]):
    for i in range(len(query)):
        query[i].content = re.sub(r"\s+", " ", query[i].content.strip().lower())
    return query


def format_question_details(similar_documents: list):
    questions_str = ""

    for i, doc in enumerate(similar_documents):
        formatted_text = (
            f"Question: {doc['question_body']}\n"
            f"Topic: {doc['topic']}\n"
            f"Sub-topic: {doc['sub_topic']}\n"
            f"Relevance Score: {doc['score']}\n"
            f"Link: {_format_question_url(doc)}"
        )
        questions_str += f"{i+1}. {formatted_text}\n\n"

    return questions_str


def format_first_question_xml(similar_documents: list):
    first_doc = similar_documents[0]

    questions_str = (
        f"<question>{first_doc['question_body']}</question>\n"
        f"<topic>{first_doc['topic']}</topic>\n"
        f"<sub_topic>{first_doc['sub_topic']}</sub_topic>\n"
        f"<link>{_format_question_url(first_doc)}</link>"
    )
    return questions_str


def _format_question_url(question):
    # append page number to filepath
    filepath = f"{question['question_paper_filepath']}#page={question['page_start']}"

    # replace underscores with spaces and convert to title case
    school = question["school"].replace("_", " ").title()
    subject = question["subject"].replace("_", " ").title()
    exam_type = question["exam_type"].replace("_", " ").title()
    year = question["year"]
    paper_num = question["paper_number"]
    question_part = question["question_part"]

    # create text for hyperlink
    link_text = f"{school} {subject} {exam_type} {year} Paper {paper_num} Question {question_part}"

    # create markdown hyperlink
    link = f"[{link_text}]({filepath})"

    return link
