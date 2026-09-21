"""
Combines the three sources into a single wide table keyed on
student_id, using an outer join so that no record from any source is
silently dropped just because it doesn't appear everywhere else.

Also stamps each row with a `source` column (bonus: data lineage) that
records which of CSV / API / DATABASE actually contributed data to it.
"""

from __future__ import annotations

import pandas as pd

from app.utils.logger import get_logger

logger = get_logger(__name__)


def integrate_data(
    csv_df: pd.DataFrame, api_df: pd.DataFrame, database_df: pd.DataFrame
) -> pd.DataFrame:
    csv_df = csv_df.copy()
    api_df = api_df.copy()
    database_df = database_df.copy()

    for df in (csv_df, api_df, database_df):
        df["student_id"] = pd.to_numeric(df["student_id"], errors="coerce").astype(
            "Int64"
        )

    merged = csv_df.merge(api_df, on="student_id", how="outer", suffixes=("", "_api"))
    merged = merged.merge(
        database_df, on="student_id", how="outer", suffixes=("", "_db")
    )

    def lineage(row: pd.Series) -> str:
        tags = []
        if "age" in row and not pd.isna(row.get("age")):
            tags.append("CSV")
        if "gpa" in row and not pd.isna(row.get("gpa")):
            tags.append("API")
        if "avg_score" in row and not pd.isna(row.get("avg_score")):
            tags.append("DATABASE")
        return "+".join(tags) if tags else "UNKNOWN"

    merged["source"] = merged.apply(lineage, axis=1)

    logger.info("Integrated records: %s", len(merged))
    return merged
