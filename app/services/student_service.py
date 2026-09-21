class StudentService:
    def __init__(self, repository):
        self.repository = repository

    def register_student(
        self, student_id, full_name, age, major, gpa
    ):
        if not student_id.strip():
            raise ValueError("Student ID is required.")

        if not full_name.strip():
            raise ValueError("Student name is required.")

        if not 16 <= age <= 80:
            raise ValueError("Age must be between 16 and 80.")

        if not 0 <= gpa <= 4:
            raise ValueError("GPA must be between 0 and 4.")

        self.repository.create(
            student_id, full_name, age, major, gpa
        )
