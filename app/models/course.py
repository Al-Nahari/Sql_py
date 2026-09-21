from dataclasses import dataclass

@dataclass
class Course:
    course_code: str
    course_name: str
    credit_hours: int
