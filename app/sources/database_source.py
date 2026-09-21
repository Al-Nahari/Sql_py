"""
Source #3: SQLite database containing `courses` and `enrollments`
tables. A student can be enrolled in several courses, so extraction
joins the two tables and aggregates to one row per student_id
(average score, number of courses, course list) before it is merged
with the other two sources.
"""

from __future__ import annotations

import os
import sqlite3

import pandas as pd

from app.utils.logger import get_logger

logger = get_logger(__name__)

_COURSES = [
    ("C001", "Data Structures", 3),
    ("C002", "Databases", 3),
    ("C003", "Machine Learning", 4),
    ("C004", "Operating Systems", 3),
    ("C005", "Networks", 3),
]

# (student_id, course_id, semester, score) - includes an invalid score
# (>100), a negative score, a missing score, and a duplicate row on
# purpose so the pipeline has real problems to clean/reject.
_ENROLLMENTS = [
    (1001, "C001", "Fall2025", 88),
    (1001, "C002", "Fall2025", 91),
    (1002, "C001", "Fall2025", 75),
    (1002, "C003", "Fall2025", 150),   # invalid: > 100
    (1003, "C002", "Fall2025", 60),
    (1004, "C001", "Fall2025", None),  # missing score
    (1005, "C004", "Fall2025", 45),
    (1006, "C002", "Fall2025", 82),
    (1007, "C005", "Fall2025", -10),   # invalid: negative
    (1008, "C001", "Fall2025", 70),
    (1009, "C003", "Fall2025", 55),
    (1010, "C002", "Fall2025", 90),
    (1010, "C002", "Fall2025", 90),    # duplicate enrollment
    (1011, "C004", "Fall2025", 40),
    (1012, "C005", "Fall2025", 66),
    (1013, "C001", "Fall2025", 58),
    (1014, "C003", "Fall2025", 77),
    (1015, "C002", "Fall2025", 83),
    (1016, "C004", "Fall2025", 95),
    (1017, "C005", "Fall2025", 61),
]


def _seed_database(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS courses (
                course_id TEXT PRIMARY KEY,
                course_name TEXT NOT NULL,
                credit_hours INTEGER NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS enrollments (
                enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_id TEXT NOT NULL,
                semester TEXT NOT NULL,
                score REAL
            )
            """
        )
        cur.executemany(
            "INSERT OR IGNORE INTO courses (course_id, course_name, credit_hours) "
            "VALUES (?, ?, ?)",
            _COURSES,
        )
        cur.executemany(
            "INSERT INTO enrollments (student_id, course_id, semester, score) "
            "VALUES (?, ?, ?, ?)",
            _ENROLLMENTS,
        )
        conn.commit()
    finally:
        conn.close()


def extract_database(db_path: str) -> pd.DataFrame:
    """Return one row per student_id with aggregated enrollment data.

    Columns: student_id, courses_count, avg_score, courses.
    """
    logger.info("Database extraction started")

    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    if not os.path.exists(db_path):
        logger.info("students.db not found, seeding demo data at %s", db_path)
        _seed_database(db_path)

    conn = sqlite3.connect(db_path)
    try:
        query = """
            SELECT
                e.student_id AS student_id,
                e.course_id AS course_id,
                c.course_name AS course_name,
                e.semester AS semester,
                e.score AS score
            FROM enrollments e
            JOIN courses c ON e.course_id = c.course_id
        """
        raw = pd.read_sql_query(query, conn)
    finally:
        conn.close()

    logger.info("Database records: %s", len(raw))

    before = len(raw)
    raw = raw.drop_duplicates(subset=["student_id", "course_id", "semester"])
    removed = before - len(raw)
    if removed:
        logger.info("Removed %s duplicate enrollment rows", removed)

    aggregated = (
        raw.groupby("student_id")
        .agg(
            courses_count=("course_id", "count"),
            avg_score=("score", "mean"),
            courses=("course_name", lambda names: "; ".join(sorted(set(names)))),
        )
        .reset_index()
    )
    return aggregated
