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
