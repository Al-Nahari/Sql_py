"""
Entry point. Wires the Extract -> Validate -> Integrate -> Transform ->
Final Validate -> Load pipeline together, following the structure
requested in the assignment (section 16).

Run with:
    python main.py
"""

from __future__ import annotations

from app.sources.csv_source import extract_csv
from app.sources.api_source import extract_api
from app.sources.database_source import extract_database
from app.transformation.cleaner import clean_csv, clean_api, clean_database
from app.transformation.integration import integrate_data
from app.transformation.transformer import transform_data
from app.validation.quality import validate_sources, validate_final_data
from app.output.csv_writer import save_processed_data, save_rejected_data
from app.utils.config import load_config, resolve_path
from app.utils.logger import get_logger
from app.utils.metrics import PipelineMetrics

logger = get_logger(__name__)


def run_pipeline() -> PipelineMetrics:
    config = load_config()
    metrics = PipelineMetrics()

    # ---------- Extract ----------
    csv_data = extract_csv(resolve_path(config["paths"]["raw_csv"]))
    api_data = extract_api(
        host=config["api"]["host"],
        port=config["api"]["port"],
        path=config["api"]["path"],
        timeout=config["api"]["timeout"],
        retries=config["api"]["retries"],
        retry_backoff_seconds=config["api"]["retry_backoff_seconds"],
    )
    database_data = extract_database(resolve_path(config["paths"]["database"]))

    metrics.csv_records = len(csv_data)
    metrics.api_records = len(api_data)
    metrics.database_records = len(database_data)

    # ---------- Validate (per-source sanity check) ----------
    validate_sources(csv_data, api_data, database_data)

    # ---------- Clean ----------
    csv_data = clean_csv(csv_data, metrics=metrics)
    api_data = clean_api(api_data, metrics=metrics)
    database_data = clean_database(database_data, metrics=metrics)

    # ---------- Integrate ----------
    integrated_data = integrate_data(csv_data, api_data, database_data)
    metrics.integrated_records = len(integrated_data)

    # ---------- Transform ----------
    transformed_data = transform_data(integrated_data)

    # ---------- Final Validation ----------
    valid_data, rejected_data = validate_final_data(
        transformed_data, config["validation"]
    )
    metrics.valid_records = len(valid_data)
    metrics.rejected_records = len(rejected_data)

    # ---------- Load ----------
    save_processed_data(valid_data, resolve_path(config["paths"]["processed_output"]))
    save_rejected_data(rejected_data, resolve_path(config["paths"]["rejected_output"]))

    summary = metrics.as_summary_text()
    logger.info("\n%s", summary)
    print(summary)

    return metrics


if __name__ == "__main__":
    run_pipeline()
