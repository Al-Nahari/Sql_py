def validate_rows(rows):
    required = {
        "student_id", "student_name", "age", "major", "gpa",
        "course_code", "course_name", "credit_hours", "semester",
        "assessment_type", "max_score", "score",
        "score_percentage", "grade"
    }

    errors = []

    for number, row in enumerate(rows, start=1):
        missing = required - row.keys()

        if missing:
            errors.append(
                f"Row {number}: missing {sorted(missing)}"
            )

        if not 0 <= float(row["gpa"]) <= 4:
            errors.append(f"Row {number}: invalid GPA")

        if not 16 <= int(row["age"]) <= 80:
            errors.append(f"Row {number}: invalid age")

        if not 0 <= float(row["score_percentage"]) <= 100:
            errors.append(
                f"Row {number}: invalid score percentage"
            )

    if errors:
        raise ValueError(
            "ETL validation failed:\n" + "\n".join(errors)
        )

    return True
