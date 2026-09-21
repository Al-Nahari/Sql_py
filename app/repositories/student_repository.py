class StudentRepository:
    def __init__(self, connection):
        self.connection = connection

    def create(self, student_id, full_name, age, major, gpa):
        self.connection.execute(
            """
            INSERT INTO students
            (student_id, full_name, age, major, gpa)
            VALUES (?, ?, ?, ?, ?)
            """,
            (student_id, full_name, age, major, gpa)
        )
        self.connection.commit()

    def get(self, student_id):
        return self.connection.execute(
            "SELECT * FROM students WHERE student_id = ?",
            (student_id,)
        ).fetchone()

    def list_all(self):
        return self.connection.execute(
            "SELECT * FROM students ORDER BY student_id"
        ).fetchall()

    def update(self, student_id, **fields):
        allowed = {"full_name", "age", "major", "gpa"}
        fields = {k: v for k, v in fields.items() if k in allowed}

        if not fields:
            raise ValueError("No valid fields supplied.")

        assignments = ", ".join(
            f"{key} = ?" for key in fields
        )

        self.connection.execute(
            f"""
            UPDATE students
            SET {assignments}
            WHERE student_id = ?
            """,
            (*fields.values(), student_id)
        )
        self.connection.commit()

    def delete(self, student_id):
        self.connection.execute(
            "DELETE FROM students WHERE student_id = ?",
            (student_id,)
        )
        self.connection.commit()
