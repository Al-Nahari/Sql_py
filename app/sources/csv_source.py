"""
Source #1: CSV file containing the base student roster
(student_id, student_name, age, major, city).
"""

from __future__ import annotations

import os

import pandas as pd

from app.utils.logger import get_logger

logger = get_logger(__name__)


def extract_csv(csv_path: str) -> pd.DataFrame:
    """Read the raw students CSV file into a DataFrame.

    Raises FileNotFoundError with a clear message if the file is missing,
    so the caller can decide whether to abort the pipeline.
    """
    logger.info("CSV extraction started")

    if not os.path.exists(csv_path):
        logger.error("CSV file not found at %s", csv_path)
        raise FileNotFoundError(f"CSV source file not found: {csv_path}")

    try:
        df = pd.read_csv(csv_path, dtype={"student_id": "Int64"})
    except pd.errors.EmptyDataError:
        logger.error("CSV file is empty: %s", csv_path)
        raise
    except pd.errors.ParserError as exc:
        logger.error("Failed to parse CSV file %s: %s", csv_path, exc)
        raise

    logger.info("CSV records: %s", len(df))
    return df
