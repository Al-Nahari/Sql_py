QUERY = """
SELECT
    s.student_id,
    s.full_name,
    s.age,
    s.major,
    s.gpa,
    c.course_code,
    c.course_name,
    c.credit_hours,
    e.semester,
    a.assessment_type,
    a.max_score,
    a.score
FROM assessments AS a
JOIN enrollments AS e
    ON e.enrollment_id = a.enrollment_id
JOIN students AS s
    ON s.student_id = e.student_id
JOIN courses AS c
    ON c.course_code = e.course_code
ORDER BY
    s.student_id,
    c.course_code,
    a.assessment_id
"""

def extract_rows(connection):
    return connection.execute(QUERY).fetchall()
