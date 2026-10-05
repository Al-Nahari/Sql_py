from __future__ import annotations

import pandas as pd
from pymongo import MongoClient

from app.utils.logger import get_logger

logger = get_logger(__name__)


def extract_mongodb(
    uri: str,
    database_name: str,
    collection_name: str,
    server_selection_timeout_ms: int = 5000,
) -> pd.DataFrame:
    """Read student records from MongoDB, excluding Mongo's internal _id."""
    logger.info("MongoDB extraction started: %s.%s", database_name, collection_name)
    client = MongoClient(
        uri,
        serverSelectionTimeoutMS=server_selection_timeout_ms,
    )
    try:
        records = list(client[database_name][collection_name].find({}))
    finally:
        client.close()

    if not records:
        logger.info("MongoDB records: 0")
        return pd.DataFrame(columns=["student_id"])

    student_records = []
    for record in records:
        nested_students = record.get("students")
        if isinstance(nested_students, list):
            student_records.extend(
                student for student in nested_students if isinstance(student, dict)
            )
        elif "student_id" in record:
            student_records.append(record)

    if not student_records:
        logger.warning(
            "MongoDB collection %s.%s contains documents but no student records",
            database_name,
            collection_name,
        )
        return pd.DataFrame(columns=["student_id"])

    data = pd.DataFrame(student_records).drop(columns="_id", errors="ignore")
    if "full_name" in data.columns and "student_name" not in data.columns:
        data = data.rename(columns={"full_name": "student_name"})

    logger.info("MongoDB records: %s", len(data))
    return data