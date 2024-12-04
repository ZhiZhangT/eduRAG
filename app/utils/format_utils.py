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


def format_answer(text):
    # used to remove the 'answer: ' (case-insensitive) prefix from the generated answer
    parts = re.split(r"answer:\s*", text, flags=re.IGNORECASE)
    text = parts[1] if len(parts) > 1 else text

    # remove all whitespace characters (spaces, tabs, newlines)
    text = re.sub(r"\s+", "", text)

    return text


def format_python_script(text):
    # Split the string into lines
    lines = text.split("\n")

    # Remove lines that contain ````
    lines = [line for line in lines if "```" not in line]

    # Join lines back together
    cleaned_code = "\n".join(lines)

    return cleaned_code


def format_first_question_xml(similar_documents: list):
    first_doc = similar_documents[0]

    questions_str = (
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


if __name__ == "__main__":
    FILEPATH = "output/chij_st_theresas_convent_additional_mathematics_preliminary_exam_2023_2_5ai_01JE27KVRYKBVKR2XE60WVQM9J_0.py"
    FILEPATH_FORMATTED = "output/chij_st_theresas_convent_additional_mathematics_preliminary_exam_2023_2_5ai_01JE27KVRYKBVKR2XE60WVQM9J_0_formatted.py"
    # First read the file
    with open(FILEPATH, "r") as file:
        text = file.read()

    # Format the text
    formatted_text = format_python_script(text)

    # Then write back to the file
    with open(FILEPATH_FORMATTED, "w") as file:
        file.write(formatted_text)
