from __future__ import annotations

import json

import pandas as pd
from pymongo import MongoClient, ReplaceOne

from app.utils.logger import get_logger

logger = get_logger(__name__)


def save_mongodb_data(
    df: pd.DataFrame,
    uri: str,
    database_name: str,
    collection_name: str,
    server_selection_timeout_ms: int = 5000,
) -> int:
    """Upsert valid student records into MongoDB by student_id."""
    if df.empty:
        logger.info("No valid records to save to MongoDB")
        return 0
    if "student_id" not in df.columns:
        raise ValueError("MongoDB records must include student_id.")

    records = json.loads(df.to_json(orient="records", date_format="iso"))
    if any(record["student_id"] is None for record in records):
        raise ValueError("MongoDB records must have a non-null student_id.")

    operations = [
        ReplaceOne({"student_id": record["student_id"]}, record, upsert=True)
        for record in records
    ]

    client = MongoClient(
        uri,
        serverSelectionTimeoutMS=server_selection_timeout_ms,
    )
    try:
        client[database_name][collection_name].bulk_write(
            operations,
            ordered=False,
        )
    finally:
        client.close()

    logger.info(
        "MongoDB dataset saved: %s.%s (%s records)",
        database_name,
        collection_name,
        len(records),
    )
    return len(records)