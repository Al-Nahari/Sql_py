from app.database.schema import initialize_database
from app.repositories.student_repository import StudentRepository
from app.repositories.course_repository import CourseRepository
from app.repositories.enrollment_repository import EnrollmentRepository
from app.repositories.assessment_repository import AssessmentRepository
from app.etl.pipeline import run_pipeline

def seed_demo_data(student_repo, course_repo, enrollment_repo, assessment_repo):
    students = [
        ("STU001", "Ahmed Ali", 21, "Computer Science", 3.45),
        ("STU002", "Sara Mohammed", 22, "Artificial Intelligence", 3.82),
        ("STU003", "Omar Hassan", 20, "Information Systems", 2.91),
        ("STU004", "Noura Salem", 23, "Computer Science", 3.67),
    ]
    courses = [
        ("CS101", "Python Programming", 3),
        ("DB201", "Database Systems", 3),
        ("DE301", "Data Engineering", 4),
    ]

    for student in students:
        try:
            student_repo.create(*student)
        except Exception:
            pass

    for course in courses:
        try:
            course_repo.create(*course)
        except Exception:
            pass

    enrollments = [
        ("STU001", "CS101"), ("STU001", "DB201"),
        ("STU002", "CS101"), ("STU002", "DE301"),
        ("STU003", "DB201"),
        ("STU004", "CS101"), ("STU004", "DE301"),
    ]

    for student_id, course_code in enrollments:
        try:
            enrollment_id = enrollment_repo.create(
                student_id, course_code, "2026-Fall"
            )
            assessment_repo.create(enrollment_id, "Midterm", 25, 22)
            assessment_repo.create(enrollment_id, "Final", 50, 42)
            assessment_repo.create(enrollment_id, "Assignment", 25, 23)
        except Exception:
            pass

def main():
    conn = initialize_database()

    student_repo = StudentRepository(conn)
    course_repo = CourseRepository(conn)
    enrollment_repo = EnrollmentRepository(conn)
    assessment_repo = AssessmentRepository(conn)

    seed_demo_data(
        student_repo, course_repo, enrollment_repo, assessment_repo
    )

    # Demonstrate UPDATE.
    student_repo.update("STU003", gpa=3.05)

    # Demonstrate DELETE using a temporary record.
    course_repo.create("TMP999", "Temporary Course", 1)
    course_repo.delete("TMP999")

    # Run ETL pipeline.
    output_file = run_pipeline(conn)

    conn.close()

    print("Application completed successfully.")
    print(f"Processed CSV: {output_file}")

if __name__ == "__main__":
    main()
