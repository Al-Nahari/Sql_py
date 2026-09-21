"""
Covers the 8 test cases requested in the assignment (section 18):
  1. CSV loaded
  2. API reachable
  3. SQLite data extracted
  4. Duplicates removed
  5. Missing values handled
  6. Invalid data rejected
  7. Sources merged successfully
  8. final_dataset.csv created
"""

from __future__ import annotations

import os
import shutil
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.sources.csv_source import extract_csv
from app.sources.api_source import extract_api
from app.sources.database_source import extract_database
from app.transformation.cleaner import clean_csv, clean_api
from app.transformation.integration import integrate_data
from app.transformation.transformer import transform_data
from app.validation.quality import validate_final_data
from app.output.csv_writer import save_processed_data, save_rejected_data
from app.utils.config import load_config, resolve_path


class TestPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = load_config()
        cls.test_db_path = resolve_path("database/test_students.db")
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)

        cls.csv_df = extract_csv(resolve_path(cls.config["paths"]["raw_csv"]))
        cls.api_df = extract_api(
            host=cls.config["api"]["host"],
            port=cls.config["api"]["port"],
            path=cls.config["api"]["path"],
            timeout=cls.config["api"]["timeout"],
            retries=cls.config["api"]["retries"],
            retry_backoff_seconds=cls.config["api"]["retry_backoff_seconds"],
        )
        cls.db_df = extract_database(cls.test_db_path)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)

    # Test 1
    def test_csv_loaded(self):
        self.assertGreater(len(self.csv_df), 0)
        self.assertIn("student_id", self.csv_df.columns)

    # Test 2
    def test_api_reachable(self):
        self.assertGreater(len(self.api_df), 0)
        self.assertIn("gpa", self.api_df.columns)

    # Test 3
    def test_database_extracted(self):
        self.assertGreater(len(self.db_df), 0)
        self.assertIn("avg_score", self.db_df.columns)

    # Test 4
    def test_duplicates_removed(self):
        cleaned = clean_csv(self.csv_df.copy())
        raw_dupes = self.csv_df.duplicated().sum()
        self.assertGreater(raw_dupes, 0)  # the raw fixture does contain a dupe
        self.assertEqual(cleaned.duplicated().sum(), 0)

    # Test 5
    def test_missing_values_handled(self):
        cleaned_csv = clean_csv(self.csv_df.copy())
        self.assertFalse(
            cleaned_csv["student_name"].isna().any()
            or (cleaned_csv["student_name"] == "").any()
        )
        cleaned_api = clean_api(self.api_df.copy())
        self.assertFalse(cleaned_api["gpa"].isna().any())

    # Test 6
    def test_invalid_records_rejected(self):
        cleaned_csv = clean_csv(self.csv_df.copy())
        cleaned_api = clean_api(self.api_df.copy())
        integrated = integrate_data(cleaned_csv, cleaned_api, self.db_df)
        transformed = transform_data(integrated)
        valid_df, rejected_df = validate_final_data(
            transformed, self.config["validation"]
        )
        self.assertGreater(len(rejected_df), 0)
        self.assertIn("error_reason", rejected_df.columns)

    # Test 7
    def test_sources_merged(self):
        cleaned_csv = clean_csv(self.csv_df.copy())
        cleaned_api = clean_api(self.api_df.copy())
        integrated = integrate_data(cleaned_csv, cleaned_api, self.db_df)
        self.assertIn("gpa", integrated.columns)
        self.assertIn("age", integrated.columns)
        self.assertIn("avg_score", integrated.columns)
        self.assertGreaterEqual(len(integrated), len(cleaned_csv))

    # Test 8
    def test_final_dataset_created(self):
        cleaned_csv = clean_csv(self.csv_df.copy())
        cleaned_api = clean_api(self.api_df.copy())
        integrated = integrate_data(cleaned_csv, cleaned_api, self.db_df)
        transformed = transform_data(integrated)
        valid_df, rejected_df = validate_final_data(
            transformed, self.config["validation"]
        )

        out_path = resolve_path("data/processed/_test_final_dataset.csv")
        rejected_path = resolve_path("data/rejected/_test_rejected_records.csv")
        save_processed_data(valid_df, out_path)
        save_rejected_data(rejected_df, rejected_path)

        self.assertTrue(os.path.exists(out_path))
        self.assertTrue(os.path.exists(rejected_path))

        os.remove(out_path)
        os.remove(rejected_path)


if __name__ == "__main__":
    unittest.main()
