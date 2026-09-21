"""
Transform stage: standardizes column names, converts data types, and
adds derived columns (performance_level, attendance_status) that make
the final dataset immediately usable for reporting/BI without any
further prep.
"""

from __future__ import annotations

import re

import pandas as pd

from app.utils.logger import get_logger

logger = get_logger(__name__)


def _standardize_column_name(name: str) -> str:
    """StudentID / Student Name / studentID -> student_id / student_name."""
    name = re.sub(r"(?<!^)(?=[A-Z])", "_", name)  # camelCase -> camel_Case
    name = name.strip().lower()
    name = re.sub(r"[\s\-]+", "_", name)
    name = re.sub(r"_+", "_", name)
    return name


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={col: _standardize_column_name(col) for col in df.columns})
    return df


def convert_types(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "student_id" in df.columns:
        df["student_id"] = pd.to_numeric(df["student_id"], errors="coerce").astype(
            "Int64"
        )
    if "age" in df.columns:
        df["age"] = pd.to_numeric(df["age"], errors="coerce")
    if "gpa" in df.columns:
        df["gpa"] = pd.to_numeric(df["gpa"], errors="coerce")
    if "attendance" in df.columns:
        df["attendance"] = pd.to_numeric(df["attendance"], errors="coerce")
    if "avg_score" in df.columns:
        df["avg_score"] = pd.to_numeric(df["avg_score"], errors="coerce").round(2)
    if "courses_count" in df.columns:
        df["courses_count"] = pd.to_numeric(
            df["courses_count"], errors="coerce"
        ).astype("Int64")

    return df


def _performance_level(gpa) -> str:
    if pd.isna(gpa):
        return "Unknown"
    if gpa >= 3.5:
        return "Excellent"
    if gpa >= 3.0:
        return "Very Good"
    if gpa >= 2.5:
        return "Good"
    if gpa >= 2.0:
        return "Acceptable"
    return "At Risk"


def _attendance_status(attendance) -> str:
    if pd.isna(attendance):
        return "Unknown"
    return "Good" if attendance >= 75 else "Low"


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "gpa" in df.columns:
        df["performance_level"] = df["gpa"].apply(_performance_level)
    if "attendance" in df.columns:
        df["attendance_status"] = df["attendance"].apply(_attendance_status)
    return df


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Transformation started")
    df = standardize_columns(df)
    df = convert_types(df)
    df = add_derived_columns(df)
    logger.info("Transformation completed")
    return df
