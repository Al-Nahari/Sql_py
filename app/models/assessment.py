from dataclasses import dataclass

@dataclass
class Assessment:
    assessment_id: int | None
    enrollment_id: int
    assessment_type: str
    max_score: float
    score: float
