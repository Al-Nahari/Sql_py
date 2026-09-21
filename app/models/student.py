from dataclasses import dataclass

@dataclass
class Student:
    student_id: str
    full_name: str
    age: int
    major: str
    gpa: float
