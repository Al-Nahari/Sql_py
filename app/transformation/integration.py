"""
Combines the three sources into a single wide table keyed on
student_id, using an outer join so that no record from any source is
silently dropped just because it doesn't appear everywhere else.

Also stamps each row with a `source` column recording which input sources
actually contained that student's record.
"""

from __future__ import annotations

import pandas as pd

from app.utils.logger import get_logger

logger = get_logger(__name__)


def integrate_data(
    csv_df: pd.DataFrame,
    api_df: pd.DataFrame,
    database_df: pd.DataFrame,
    mongodb_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    csv_df = csv_df.copy()
    api_df = api_df.copy()
    database_df = database_df.copy()
    mongodb_df = (
        mongodb_df.copy()
        if mongodb_df is not None
        else pd.DataFrame(columns=["student_id"])
    )

    source_frames = {
        "CSV": csv_df,
        "API": api_df,
        "DATABASE": database_df,
        "MONGODB": mongodb_df,
    }
    for source, df in source_frames.items():
        df[f"__{source.lower()}_present"] = True
        df["student_id"] = pd.to_numeric(df["student_id"], errors="coerce").astype(
            "Int64"
        )

    merged = csv_df.merge(api_df, on="student_id", how="outer", suffixes=("", "_api"))
    merged = merged.merge(
        database_df, on="student_id", how="outer", suffixes=("", "_db")
    )
    merged = merged.merge(
        mongodb_df, on="student_id", how="outer", suffixes=("", "_mongodb")
    )

    mongodb_suffix = "_mongodb"
    for column in [column for column in merged.columns if column.endswith(mongodb_suffix)]:
        original_column = column[: -len(mongodb_suffix)]
        if original_column in merged.columns:
            merged[original_column] = merged[original_column].combine_first(
                merged[column]
            )
            merged = merged.drop(columns=column)
        else:
            merged = merged.rename(columns={column: original_column})

    def lineage(row: pd.Series) -> str:
        tags = []
        for source in source_frames:
            present = row.get(f"__{source.lower()}_present")
            if not pd.isna(present) and bool(present):
                tags.append(source)
        return "+".join(tags) if tags else "UNKNOWN"

    merged["source"] = merged.apply(lineage, axis=1)
    merged = merged.drop(
        columns=[f"__{source.lower()}_present" for source in source_frames]
    )

    logger.info("Integrated records: %s", len(merged))
    return merged