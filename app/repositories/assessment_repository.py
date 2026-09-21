class AssessmentRepository:
    def __init__(self, connection):
        self.connection = connection

    def create(self, enrollment_id, assessment_type, max_score, score):
        cursor = self.connection.execute(
            """
            INSERT INTO assessments
            (enrollment_id, assessment_type, max_score, score)
            VALUES (?, ?, ?, ?)
            """,
            (enrollment_id, assessment_type, max_score, score)
        )
        self.connection.commit()
        return cursor.lastrowid

    def get(self, assessment_id):
        return self.connection.execute(
            "SELECT * FROM assessments WHERE assessment_id = ?",
            (assessment_id,)
        ).fetchone()

    def list_all(self):
        return self.connection.execute(
            "SELECT * FROM assessments ORDER BY assessment_id"
        ).fetchall()

    def update(self, assessment_id, **fields):
        allowed = {"assessment_type", "max_score", "score"}
        fields = {k: v for k, v in fields.items() if k in allowed}

        if not fields:
            raise ValueError("No valid fields supplied.")

        assignments = ", ".join(
            f"{key} = ?" for key in fields
        )

        self.connection.execute(
            f"""
            UPDATE assessments
            SET {assignments}
            WHERE assessment_id = ?
            """,
            (*fields.values(), assessment_id)
        )
        self.connection.commit()

    def delete(self, assessment_id):
        self.connection.execute(
            "DELETE FROM assessments WHERE assessment_id = ?",
            (assessment_id,)
        )
        self.connection.commit()
