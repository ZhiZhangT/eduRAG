import re


def clean_meta_info(meta_info):
    # Remove special characters, strip whitespace, and convert to lowercase
    cleaned_meta_info = {}
    for key, value in meta_info.items():
        # Remove special characters using regex
        value = re.sub(r"[^\w\s]", "", value)
        # Strip whitespace and convert to lowercase
        value = value.strip().lower()
        cleaned_meta_info[key] = value
        # Replace spaces with underscores
        cleaned_meta_info[key] = value.replace(" ", "_")
    return cleaned_meta_info


def convert_exam_type(exam_type):
    # Map exam type to enum values
    exam_type_mapping = {
        "preliminary examination": "prelim",
        "mid year examination": "mid_year",
        "final year examination": "final_year",
        "test": "test",
    }
    return exam_type_mapping.get(exam_type, exam_type)
