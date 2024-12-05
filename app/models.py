import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict, model_validator
from enum import Enum
from pydantic import BaseModel
from enum import Enum


class SubjectEnum(str, Enum):
    ADDITIONAL_MATHEMATICS = "additional_mathematics"
    ELEMENTARY_MATHEMATICS = "elementary_mathematics"
    H2_MATHEMATICS = "h2_mathematics"

    @classmethod
    def _missing_(cls, value):
        value = value.lower().replace(" ", "_")
        for member in cls:
            print(f"member.value: {member.value}")
            if member.value.lower() == value:
                return member
        return None


class LevelEnum(str, Enum):
    O_LEVEL = "o_level"
    A_LEVEL = "a_level"


class ExamTypeEnum(str, Enum):
    PRELIM = "preliminary_exam"
    FINAL = "final_exam"
    MID_YEAR = "mid_year_exam"
    # Add more exam types as needed


class AMathTopicEnum(str, Enum):
    QUADRATIC_FUNCTIONS_EQUATIONS_AND_INEQUALITIES = (
        "Quadratic Functions, Equations and Inequalities"
    )
    SURDS = "Surds"
    POLYNOMIALS_CUBIC_EQUATIONS_AND_PARTIAL_FRACTIONS = (
        "Polynomials, cubic equations and partial fractions"
    )
    BINOMIAL_THEOREM_AND_ITS_APPLICATION = "Binomial theorem and its application"
    EXPONENTIAL_AND_LOGARITHMIC_FUNCTIONS = "Exponential and logarithmic functions"
    COORDINATE_GEOMETRY = "Coordinate geometry"
    LINEAR_LAW = "Linear law"
    TRIGONOMETRIC_FUNCTIONS_AND_EQUATIONS = "Trigonometric functions and equations"
    TRIGONOMETRIC_IDENTITIES_AND_FORMULAE = "Trigonometric identities and formulae"
    GRADIENTS_DERIVATIVES_AND_DIFFERENTIATION_TECHNIQUES = (
        "Gradients, derivatives and differentiation techniques"
    )
    APPLICATIONS_OF_DIFFERENTIATION = "Applications of differentiation"
    DIFFERENTIATION_OF_TRIGONOMETRIC_LOGARITHMIC_AND_EXPONENTIAL_FUNCTIONS_AND_APPLICATIONS = "Differentiation of trigonometric, logarithmic, and exponential functions and their applications"
    INTEGRATION = "Integration"
    APPLICATIONS_OF_INTEGRATION = "Applications of integration"
    KINEMATICS = "Kinematics"
    PROOFS_IN_PLANE_GEOMETRY = "Proofs in plane geometry"


class EMathTopicEnum(str, Enum):
    NUMBERS_AND_OPERATIONS = "Numbers and their operations"
    RATIO_AND_PROPORTION = "Ratio and proportion"
    PERCENTAGE = "Percentage"
    RATE_AND_SPEED = "Rate and speed"
    ALGEBRAIC_EXPRESSIONS_AND_FORMULAE = "Algebraic expressions and formulae"
    FUNCTIONS_AND_GRAPHS = "Functions and graphs"
    EQUATIONS_AND_INEQUALITIES = "Equations and inequalities"
    SET_LANGUAGE_AND_NOTATION = "Set language and notation"
    MATRICES = "Matrices"
    PROBLEMS_IN_REAL_WORLD_CONTEXTS = "Problems in real-world contexts"
    ANGLES_TRIANGLES_AND_POLYGONS = "Angles, triangles and polygons"
    CONGRUENCE_AND_SIMILARITY = "Congruence and similarity"
    PROPERTIES_OF_CIRCLES = "Properties of circles"
    PYTHAGORAS_THEOREM_AND_TRIGONOMETRY = "Pythagoras’ theorem and trigonometry"
    MENSURATION = "Mensuration"
    COORDINATE_GEOMETRY = "Coordinate geometry"
    VECTORS_IN_2_DIMENSIONS = "Vectors in 2 dimensions"
    DATA_ANALYSIS = "Data analysis"
    PROBABILITY = "Probability"


class DifficultyEnum(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    DIFFICULT = "difficult"


class MetaInfo(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, strict=True)

    subject: SubjectEnum = Field(..., description="Subject cannot be empty")
    school: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="School name must be between 1 and 100 characters",
    )
    level: LevelEnum = Field(..., description="Level cannot be empty")
    year: str = Field(
        ..., pattern="^[0-9]{4}$", description="Year must be a 4-digit number"
    )
    exam_type: ExamTypeEnum = Field(..., description="Exam type cannot be empty")
    paper: str = Field(
        ..., pattern="^[1-4]$", description="Paper must be a number between 1 and 4"
    )

    @model_validator(mode="before")
    @classmethod
    def clean_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        cleaned_data = _clean_meta_info(data)
        # convert string values to Enum values for schema validation purposes
        if "subject" in cleaned_data:
            cleaned_data["subject"] = SubjectEnum(cleaned_data["subject"])
        if "level" in cleaned_data:
            cleaned_data["level"] = LevelEnum(cleaned_data["level"])
        if "exam_type" in cleaned_data:
            cleaned_data["exam_type"] = ExamTypeEnum(cleaned_data["exam_type"])
        return cleaned_data

    @field_validator("*")
    @classmethod
    def check_not_empty(cls, v, info):
        if isinstance(v, str) and not v.strip():
            raise ValueError(f"{info.field_name} cannot be empty")
        return v


class QuestionItem(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, strict=True)

    question: str = Field(
        ..., min_length=1, description="Question text cannot be empty"
    )
    page_start: int = Field(
        ..., ge=1, description="Page start must be greater than or equal to 1"
    )
    page_end: int = Field(
        ..., ge=1, description="Page end must be greater than or equal to 1"
    )
    category: str = Field(..., min_length=1, description="Category cannot be empty")
    question_type: str = Field(..., description="Question type must be valid")
    question_number: str = Field(
        ..., min_length=1, description="Question number cannot be empty"
    )
    question_part: str = Field(
        ..., min_length=1, description="Question part cannot be empty"
    )
    marks: int = Field(
        ..., ge=1, description="Marks must be greater than or equal to 1"
    )
    difficulty: DifficultyEnum = Field(..., description="Difficulty cannot be empty")

    @model_validator(mode="before")
    @classmethod
    def clean_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        cleaned_data = data.copy()
        # ensure that each question_number is of str type
        cleaned_data["question_number"] = str(data["question_number"])
        # convert string values to Enum values for schema validation purposes
        # NOTE: the 'difficulty_level' field is renamed to 'difficulty' in the schema
        cleaned_data["difficulty"] = DifficultyEnum(data["difficulty_level"])
        return cleaned_data

    @field_validator("*")
    @classmethod
    def check_not_empty(cls, v, info):
        if isinstance(v, str) and not v.strip():
            raise ValueError(f"{info.field_name} cannot be empty")
        return v

    @field_validator("page_end")
    @classmethod
    def validate_page_range(cls, v, info):
        if "page_start" in info.data and v < info.data["page_start"]:
            raise ValueError("page_end must be greater than or equal to page_start")
        return v


class QuestionData(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, strict=True)

    meta_info: MetaInfo = Field(..., description="Meta information cannot be empty")
    questions: List[QuestionItem] = Field(
        ..., min_items=1, description="Questions list cannot be empty"
    )
    question_paper_filepath: str = Field(
        ..., min_length=1, description="Question filepath cannot be empty"
    )
    answer_paper_filepath: str

    @field_validator("*")
    @classmethod
    def check_not_empty(cls, v, info):
        if isinstance(v, str) and not v.strip():
            raise ValueError(f"{info.field_name} cannot be empty")
        return v

    @field_validator("questions")
    @classmethod
    def validate_questions_not_empty(cls, v):
        if not v:
            raise ValueError("Questions list cannot be empty")
        return v


class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class BaseModelWithRoleEncoder(BaseModel):
    class Config:
        json_encoders = {Role: lambda v: v.value}


class Message(BaseModelWithRoleEncoder):
    role: Role
    content: str


class QueryRequest(BaseModel):
    user_query: List[Message]
    subject: str = "elementary_mathematics"
    level: Optional[str] = None
    exam_type: Optional[str] = None


class GeneratedQuestion(BaseModel):
    question_text: str
    topic: str
    sub_topic: str
    steps: List[str]
    answer: str


class GeneratedPythonScript(BaseModel):
    python_script: str


class CorrectedGeneratedPythonScript(BaseModel):
    python_script: str
    final_answer: str
    is_suggested_answer_correct: bool
    reason: str
    changes_made: List[str]


class FormattedGeneratedPythonScript(BaseModel):
    python_script: str
    format_changes: List[str]


def _clean_meta_info(meta_info):
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
