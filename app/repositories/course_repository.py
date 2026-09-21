class CourseRepository:
    def __init__(self, connection):
        self.connection = connection

    def create(self, course_code, course_name, credit_hours):
        self.connection.execute(
            """
            INSERT INTO courses
            (course_code, course_name, credit_hours)
            VALUES (?, ?, ?)
            """,
            (course_code, course_name, credit_hours)
        )
        self.connection.commit()

    def get(self, course_code):
        return self.connection.execute(
            "SELECT * FROM courses WHERE course_code = ?",
            (course_code,)
        ).fetchone()

    def list_all(self):
        return self.connection.execute(
            "SELECT * FROM courses ORDER BY course_code"
        ).fetchall()

    def update(self, course_code, **fields):
        allowed = {"course_name", "credit_hours"}
        fields = {k: v for k, v in fields.items() if k in allowed}

        if not fields:
            raise ValueError("No valid fields supplied.")

        assignments = ", ".join(
            f"{key} = ?" for key in fields
        )

        self.connection.execute(
            f"""
            UPDATE courses
            SET {assignments}
            WHERE course_code = ?
            """,
            (*fields.values(), course_code)
        )
        self.connection.commit()

    def delete(self, course_code):
        self.connection.execute(
            "DELETE FROM courses WHERE course_code = ?",
            (course_code,)
        )
        self.connection.commit()
