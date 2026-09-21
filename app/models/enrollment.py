from dataclasses import dataclass

@dataclass
class Enrollment:
    enrollment_id: int | None
    student_id: str
    course_code: str
    semester: str
