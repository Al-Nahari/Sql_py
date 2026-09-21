"""
Small dataclass that accumulates pipeline metrics as each stage runs,
then prints/logs the final "PIPELINE EXECUTION SUMMARY" block.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class PipelineMetrics:
    csv_records: int = 0
    api_records: int = 0
    database_records: int = 0
    integrated_records: int = 0
    valid_records: int = 0
    rejected_records: int = 0
    duplicate_records: int = 0
    missing_values_filled: int = 0
    _start_time: float = field(default_factory=time.perf_counter)
    _elapsed_seconds: float = 0.0

    def stop_timer(self) -> None:
        self._elapsed_seconds = time.perf_counter() - self._start_time

    def as_summary_text(self) -> str:
        self.stop_timer()
        lines = [
            "-----------------------------------",
            "PIPELINE EXECUTION SUMMARY",
            "-----------------------------------",
            f"CSV Records        : {self.csv_records}",
            f"API Records        : {self.api_records}",
            f"Database Records   : {self.database_records}",
            "",
            f"Integrated Records : {self.integrated_records}",
            "",
            f"Valid Records      : {self.valid_records}",
            f"Rejected Records   : {self.rejected_records}",
            f"Duplicate Records  : {self.duplicate_records}",
            f"Missing Values Fixed: {self.missing_values_filled}",
            "",
            f"Processing Time    : {self._elapsed_seconds:.2f} seconds",
            "-----------------------------------",
        ]
        return "\n".join(lines)
