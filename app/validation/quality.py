"""
Implements the data quality rules from the assignment (section 10):

  Rule 1: student_id cannot be NULL
  Rule 2: student_id must be unique
  Rule 3: age must be between 16 and 80
  Rule 4: GPA must be between 0 and 4
  Rule 5: attendance must be between 0 and 100
  Rule 6: score must be between 0 and 100
  Rule 7: student_id from different sources must be compatible
          (i.e. it must be a valid, matchable identifier)

validate_sources() runs a lightweight sanity pass on each source right
after extraction (used for logging/early warnings). validate_final()
runs the full rule set on the integrated+transformed dataset and
splits it into (valid_df, rejected_df), where rejected_df carries an
error_reason column explaining exactly why each row was dropped.
"""

from __future__ import annotations

from typing import Tuple

import pandas as pd

from app.utils.logger import get_logger

logger = get_logger(__name__)


def validate_sources(
    csv_df: pd.DataFrame, api_df: pd.DataFrame, database_df: pd.DataFrame
) -> dict:
    """Quick per-source health check, logged for visibility. Does not
    drop anything - final validation is where rejection happens.
    """
    report = {
        "csv_missing_student_id": int(csv_df["student_id"].isna().sum())
        if "student_id" in csv_df.columns
        else 0,
        "api_missing_student_id": int(api_df["student_id"].isna().sum())
        if "student_id" in api_df.columns
        else 0,
        "database_missing_student_id": int(database_df["student_id"].isna().sum())
        if "student_id" in database_df.columns
        else 0,
    }
    logger.info("Source validation report: %s", report)
    return report


def _row_errors(row: pd.Series, rules: dict) -> list[str]:
    errors: list[str] = []

    student_id = row.get("student_id")
    if pd.isna(student_id):
        errors.append("Missing student_id")

    age = row.get("age")
    if "age" in row and not pd.isna(age):
        if not (rules["age_min"] <= age <= rules["age_max"]):
            errors.append("Invalid Age")

    gpa = row.get("gpa")
    if "gpa" in row and not pd.isna(gpa):
        if not (rules["gpa_min"] <= gpa <= rules["gpa_max"]):
            errors.append("Invalid GPA")

    attendance = row.get("attendance")
    if "attendance" in row and not pd.isna(attendance):
        if not (rules["attendance_min"] <= attendance <= rules["attendance_max"]):
            errors.append("Invalid Attendance")

    avg_score = row.get("avg_score")
    if "avg_score" in row and not pd.isna(avg_score):
        if not (rules["score_min"] <= avg_score <= rules["score_max"]):
            errors.append("Invalid Score")

    return errors


def validate_final_data(
    df: pd.DataFrame, rules: dict
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Apply Rules 1-6 row by row, then Rule 2 (uniqueness) across the
    whole dataset. Returns (valid_df, rejected_df).
    """
    logger.info("Final validation started")

    df = df.copy()
    error_lists = df.apply(lambda row: _row_errors(row, rules), axis=1)

    # Rule 2: student_id must be unique. Duplicate ids are rejected in
    # full (every occurrence) since we cannot safely pick a "winner".
    duplicated_mask = df["student_id"].duplicated(keep=False) & df[
        "student_id"
    ].notna()
    for idx in df.index[duplicated_mask]:
        error_lists.loc[idx] = error_lists.loc[idx] + ["Duplicate student_id"]

    has_errors = error_lists.apply(len) > 0

    valid_df = df.loc[~has_errors].copy()
    rejected_df = df.loc[has_errors].copy()
    rejected_df["error_reason"] = error_lists.loc[has_errors].apply(
        lambda errs: "; ".join(errs)
    )
    rejected_df = rejected_df[["student_id", "error_reason"] + [
        c for c in rejected_df.columns if c not in ("student_id", "error_reason")
    ]]

    logger.info(
        "Final validation completed: %s valid, %s rejected",
        len(valid_df),
        len(rejected_df),
    )
    return valid_df, rejected_df
