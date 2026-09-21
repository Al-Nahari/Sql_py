class EnrollmentRepository:
    def __init__(self, connection):
        self.connection = connection

    def create(self, student_id, course_code, semester):
        cursor = self.connection.execute(
            """
            INSERT INTO enrollments
            (student_id, course_code, semester)
            VALUES (?, ?, ?)
            """,
            (student_id, course_code, semester)
        )
        self.connection.commit()
        return cursor.lastrowid

    def get(self, enrollment_id):
        return self.connection.execute(
            "SELECT * FROM enrollments WHERE enrollment_id = ?",
            (enrollment_id,)
        ).fetchone()

    def list_all(self):
        return self.connection.execute(
            "SELECT * FROM enrollments ORDER BY enrollment_id"
        ).fetchall()

    def update(self, enrollment_id, **fields):
        allowed = {"student_id", "course_code", "semester"}
        fields = {k: v for k, v in fields.items() if k in allowed}

        if not fields:
            raise ValueError("No valid fields supplied.")

        assignments = ", ".join(
            f"{key} = ?" for key in fields
        )

        self.connection.execute(
            f"""
            UPDATE enrollments
            SET {assignments}
            WHERE enrollment_id = ?
            """,
            (*fields.values(), enrollment_id)
        )
        self.connection.commit()

    def delete(self, enrollment_id):
        self.connection.execute(
            "DELETE FROM enrollments WHERE enrollment_id = ?",
            (enrollment_id,)
        )
        self.connection.commit()
