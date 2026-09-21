import sqlite3
import unittest

from app.database.schema import SCHEMA
from app.repositories.student_repository import StudentRepository
from app.repositories.course_repository import CourseRepository
from app.repositories.enrollment_repository import EnrollmentRepository
from app.repositories.assessment_repository import AssessmentRepository

class TestCRUD(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.executescript(SCHEMA)

    def tearDown(self):
        self.connection.close()

    def test_crud_operations(self):
        students = StudentRepository(self.connection)
        courses = CourseRepository(self.connection)
        enrollments = EnrollmentRepository(self.connection)
        assessments = AssessmentRepository(self.connection)

        students.create(
            "S1", "Test Student", 20, "Computer Science", 3.2
        )
        self.assertIsNotNone(students.get("S1"))

        students.update("S1", gpa=3.7)
        self.assertEqual(students.get("S1")["gpa"], 3.7)

        courses.create("C1", "Database Systems", 3)

        enrollment_id = enrollments.create(
            "S1", "C1", "2026-Fall"
        )

        assessments.create(
            enrollment_id, "Final", 100, 85
        )

        assessments.delete(1)
        enrollments.delete(enrollment_id)
        courses.delete("C1")
        students.delete("S1")

        self.assertIsNone(students.get("S1"))

if __name__ == "__main__":
    unittest.main()
