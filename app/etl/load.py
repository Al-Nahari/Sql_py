import csv
from app.utils.paths import PROCESSED_DIR

OUTPUT_FILE = (
    PROCESSED_DIR / "student_academic_dataset.csv"
)

def load_csv(rows):
    if not rows:
        raise ValueError("No processed rows to export.")

    fieldnames = list(rows[0].keys())

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )
        writer.writeheader()
        writer.writerows(rows)

    return OUTPUT_FILE
