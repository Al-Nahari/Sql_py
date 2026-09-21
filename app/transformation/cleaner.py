"""
Data cleaning fixes *formatting* problems that would otherwise cause
good records to be rejected: duplicate rows, inconsistent text
(spacing/casing), and missing values that have a sensible business-rule
fix. Genuinely invalid values (out-of-range age/GPA/attendance/score)
are intentionally left alone here - they are caught later by
app/validation/quality.py and routed to rejected_records.csv, because
"clean" should never mean "silently hide bad data".
"""

from __future__ import annotations

import pandas as pd

from app.utils.logger import get_logger

logger = get_logger(__name__)


def _normalize_text_column(series: pd.Series) -> pd.Series:
    """Strip surrounding whitespace and use Title Case consistently,
    so "Sanaa", "sanaa", " SANAA " all collapse to "Sanaa".
    """
    return series.astype("string").str.strip().str.title()


def clean_csv(df: pd.DataFrame, metrics=None) -> pd.DataFrame:
    df = df.copy()

    before = len(df)
    df = df.drop_duplicates()
    duplicates_removed = before - len(df)
    if duplicates_removed:
        logger.info("Removed %s fully duplicated CSV rows", duplicates_removed)
        if metrics is not None:
            metrics.duplicate_records += duplicates_removed

    if "city" in df.columns:
        df["city"] = _normalize_text_column(df["city"])

    if "student_name" in df.columns:
        df["student_name"] = df["student_name"].astype("string").str.strip()
        missing_names = df["student_name"].isna() | (df["student_name"] == "")
        missing_count = int(missing_names.sum())
        if missing_count:
            logger.info(
                "Filling %s missing student_name value(s) with 'Unknown'",
                missing_count,
            )
            df.loc[missing_names, "student_name"] = "Unknown"
            if metrics is not None:
                metrics.missing_values_filled += missing_count

    if "major" in df.columns:
        df["major"] = df["major"].astype("string").str.strip()

    return df


def clean_api(df: pd.DataFrame, metrics=None) -> pd.DataFrame:
    df = df.copy()

    if "gpa" in df.columns:
        missing_gpa = df["gpa"].isna()
        missing_count = int(missing_gpa.sum())
        if missing_count:
            median_gpa = df["gpa"].median()
            logger.info(
                "Filling %s missing GPA value(s) with source median (%.2f). "
                "Median is used instead of the mean because GPA outliers "
                "(e.g. a mis-entered 4.9) would otherwise skew the average.",
                missing_count,
                median_gpa,
            )
            df.loc[missing_gpa, "gpa"] = median_gpa
            if metrics is not None:
                metrics.missing_values_filled += missing_count

    if "attendance" in df.columns:
        missing_attendance = df["attendance"].isna()
        missing_count = int(missing_attendance.sum())
        if missing_count:
            # Business rule: an unreported attendance value defaults to 0
            # (treated conservatively as "not attended") rather than being
            # guessed, since attendance directly affects academic status.
            logger.info(
                "Filling %s missing attendance value(s) using business rule (0)",
                missing_count,
            )
            df.loc[missing_attendance, "attendance"] = 0
            if metrics is not None:
                metrics.missing_values_filled += missing_count

    if "status" in df.columns:
        df["status"] = df["status"].astype("string").str.strip().str.title()

    return df


def clean_database(df: pd.DataFrame, metrics=None) -> pd.DataFrame:
    df = df.copy()

    if "avg_score" in df.columns:
        missing_score = df["avg_score"].isna()
        missing_count = int(missing_score.sum())
        if missing_count:
            median_score = df["avg_score"].median()
            logger.info(
                "Filling %s missing avg_score value(s) with source median (%.2f)",
                missing_count,
                median_score,
            )
            df.loc[missing_score, "avg_score"] = median_score
            if metrics is not None:
                metrics.missing_values_filled += missing_count

    return df
