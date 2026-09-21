"""Writes the final processed dataset and the rejected-records file."""

from __future__ import annotations

import os

import pandas as pd

from app.utils.logger import get_logger

logger = get_logger(__name__)


def save_processed_data(df: pd.DataFrame, output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info("Final dataset created: %s (%s records)", output_path, len(df))


def save_rejected_data(df: pd.DataFrame, output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info("Rejected records saved: %s (%s records)", output_path, len(df))
