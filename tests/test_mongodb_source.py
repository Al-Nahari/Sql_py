import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from app.sources.mongodb_source import extract_mongodb
from app.transformation.integration import integrate_data


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
            "nahari_source",
        )

        self.assertEqual(records.to_dict(orient="records"), [
            {"student_id": 2001, "student_name": "Nora"}
        ])
        collection.find.assert_called_once_with({})
        client.close.assert_called_once()

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


if __name__ == "__main__":
    unittest.main()