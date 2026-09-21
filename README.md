# Student Data Engineering Application

A modular Python application for managing student academic data with SQLite and exporting processed analytical data to CSV.

## Main tables
- `students`
- `courses`
- `enrollments`
- `assessments`

## Architecture

```text
student_data_engineering_app/
├── app/
│   ├── database/       # SQLite connection and schema
│   ├── models/         # Domain models
│   ├── repositories/   # CRUD / data-access layer
│   ├── services/       # Business logic
│   ├── etl/            # Extract → Transform → Validate → Load
│   └── utils/          # Paths and logging
├── data/
│   ├── raw/
│   └── processed/
├── tests/
├── main.py
├── database_schema.sql
└── requirements.txt
```

## Requirements

Python 3.10+.

No third-party packages are required; the application uses the Python standard library.

## Run

From the project root:

```bash
python main.py
```

The program creates the SQLite database, creates the tables, inserts demonstration data, demonstrates CRUD operations, runs the ETL pipeline, validates the transformed records, and writes:

```text
data/processed/student_academic_dataset.csv
```

## ETL flow

```text
SQLite Operational Database
          |
       Extract
          |
          v
   Join relational data
          |
      Transform
          |
          v
  Calculate percentages
  Assign letter grades
          |
       Validate
          |
          v
   Processed CSV Dataset
```

The CSV is intentionally denormalized so it can be consumed easily by analytics and machine-learning workflows.

## CRUD

Repositories provide create, read, update, and delete operations for students, courses, enrollments, and assessments.

SQL statements use parameters rather than string interpolation for user values.

## Data quality rules

- Age: 16–80
- GPA: 0–4
- Assessment score: 0–maximum score
- Foreign keys enabled
- Unique enrollment per student/course/semester
- Processed records validated before CSV export

## Test

```bash
python -m unittest discover -s tests -v
```
