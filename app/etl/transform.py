def calculate_grade(percentage):
    if percentage >= 90:
        return "A"
    if percentage >= 80:
        return "B"
    if percentage >= 70:
        return "C"
    if percentage >= 60:
        return "D"
    return "F"

def build_processed_rows(rows):
    processed = []

    for row in rows:
        max_score = float(row["max_score"])
        score = float(row["score"])

        percentage = (
            round((score / max_score) * 100, 2)
            if max_score else 0.0
        )

        processed.append({
            "student_id": row["student_id"],
            "student_name": row["full_name"],
            "age": row["age"],
            "major": row["major"],
            "gpa": row["gpa"],
            "course_code": row["course_code"],
            "course_name": row["course_name"],
            "credit_hours": row["credit_hours"],
            "semester": row["semester"],
            "assessment_type": row["assessment_type"],
            "max_score": max_score,
            "score": score,
            "score_percentage": percentage,
            "grade": calculate_grade(percentage),
        })

    return processed
