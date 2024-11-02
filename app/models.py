from pydantic import BaseModel
from typing import List


class MetaInfo(BaseModel):
    subject: str
    school: str
    year: str
    exam_type: str
    paper: str


class QuestionItem(BaseModel):
    question: str
    page_start: int
    page_end: int
    category: str
    question_type: str


class QuestionData(BaseModel):
    meta_info: MetaInfo
    questions: List[QuestionItem]
    question_filepath: str
    question_filename: str
    level: str
