import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from app.sources.mongodb_source import extract_mongodb
from app.transformation.cleaner import clean_mongodb
from app.transformation.integration import integrate_data
from app.transformation.transformer import transform_data
from app.validation.quality import validate_final_data


class TestMongoDBSource(unittest.TestCase):
    @patch("app.sources.mongodb_source.MongoClient")
    def test_extracts_documents_without_mongo_id(self, mongo_client):
        collection = MagicMock()
        collection.find.return_value = [
            {"_id": "mongo-id", "student_id": 2001, "full_name": "Nora"}
        ]
        client = mongo_client.return_value
        client.__getitem__.return_value.__getitem__.return_value = collection

        records = extract_mongodb(
            "mongodb://localhost:27017/",
            "Uinveresity",
            "nahari",
        )

        self.assertEqual(records.to_dict(orient="records"), [
            {"student_id": 2001, "student_name": "Nora"}
        ])
        collection.find.assert_called_once_with({})
        client.close.assert_called_once()

    @patch("app.sources.mongodb_source.MongoClient")
    def test_extracts_students_from_nested_json_document(self, mongo_client):
        collection = MagicMock()
        collection.find.return_value = [
            {
                "_id": "dataset-id",
                "instructors": [{"instructor_id": 1}],
                "students": [
                    {
                        "student_id": 1001,
                        "full_name": "Rami Haddad",
                        "gender": "Male",
                        "date_of_birth": "2002-08-23",
                        "city": "Aden",
                    },
                    {
                        "student_id": 1002,
                        "full_name": "Dina Salem",
                        "gender": "Female",
                        "date_of_birth": "2003-06-12",
                        "city": "Mukalla",
                    },
                ],
                "courses": [{"course_id": 101}],
            }
        ]
        client = mongo_client.return_value
        client.__getitem__.return_value.__getitem__.return_value = collection

        records = extract_mongodb(
            "mongodb://localhost:27017/",
            "Uinveresity",
            "nahari",
        )

        self.assertEqual(len(records), 2)
        self.assertEqual(records["student_id"].tolist(), [1001, 1002])
        self.assertEqual(records["student_name"].tolist(), ["Rami Haddad", "Dina Salem"])
        self.assertNotIn("_id", records.columns)
        self.assertNotIn("courses", records.columns)

    def test_lineage_includes_only_sources_with_records(self):
        csv_data = pd.DataFrame(
            [{"student_id": 1001, "student_name": "Amina", "age": 20}]
        )
        api_data = pd.DataFrame([{"student_id": 1001, "gpa": 3.5}])
        database_data = pd.DataFrame([{"student_id": 1001, "avg_score": 88}])
        mongodb_data = pd.DataFrame(
            [
                {"student_id": 1001, "major": "Computer Science"},
                {"student_id": 2001, "age": 22, "student_name": "Nora"},
            ]
        )

        merged = integrate_data(csv_data, api_data, database_data, mongodb_data)

        shared_student = merged.loc[merged["student_id"] == 1001].iloc[0]
        mongo_only_student = merged.loc[merged["student_id"] == 2001].iloc[0]
        self.assertEqual(shared_student["source"], "CSV+API+DATABASE+MONGODB")
        self.assertEqual(shared_student["major"], "Computer Science")
        self.assertEqual(mongo_only_student["source"], "MONGODB")
        self.assertEqual(mongo_only_student["age"], 22)
        self.assertFalse(any(column.startswith("__") for column in merged.columns))

    def test_mongodb_only_record_is_cleaned_and_reaches_valid_output(self):
        mongodb_data = pd.DataFrame(
            [{
                "student_id": 2001,
                "student_name": "  nora ali  ",
                "age": 22,
                "major": "  computer science  ",
                "city": " sanaa ",
                "gpa": 3.4,
                "attendance": 90,
            }]
        )
        cleaned_mongodb = clean_mongodb(mongodb_data)
        integrated = integrate_data(
            pd.DataFrame(columns=["student_id", "student_name", "age", "major", "city"]),
            pd.DataFrame(columns=["student_id", "gpa", "attendance"]),
            pd.DataFrame(columns=["student_id", "avg_score"]),
            cleaned_mongodb,
        )
        transformed = transform_data(integrated)
        valid, rejected = validate_final_data(
            transformed,
            {
                "age_min": 16,
                "age_max": 80,
                "gpa_min": 0,
                "gpa_max": 4,
                "attendance_min": 0,
                "attendance_max": 100,
                "score_min": 0,
                "score_max": 100,
            },
        )

        self.assertEqual(len(valid), 1)
        self.assertEqual(len(rejected), 0)
        self.assertEqual(valid.iloc[0]["source"], "MONGODB")
        self.assertEqual(valid.iloc[0]["student_name"], "nora ali")
        self.assertEqual(valid.iloc[0]["major"], "computer science")
        self.assertEqual(valid.iloc[0]["city"], "Sanaa")


if __name__ == "__main__":
    unittest.main()