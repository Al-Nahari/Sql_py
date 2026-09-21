CREATE TABLE students (
    student_id TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    age INTEGER NOT NULL CHECK(age BETWEEN 16 AND 80),
    major TEXT NOT NULL,
    gpa REAL NOT NULL CHECK(gpa BETWEEN 0 AND 4)
);

CREATE TABLE courses (
    course_code TEXT PRIMARY KEY,
    course_name TEXT NOT NULL,
    credit_hours INTEGER NOT NULL CHECK(credit_hours BETWEEN 1 AND 6)
);

CREATE TABLE enrollments (
    enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    course_code TEXT NOT NULL,
    semester TEXT NOT NULL,
    enrollment_date TEXT NOT NULL DEFAULT CURRENT_DATE,
    UNIQUE(student_id, course_code, semester),
    FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY(course_code) REFERENCES courses(course_code) ON DELETE RESTRICT
);

CREATE TABLE assessments (
    assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id INTEGER NOT NULL,
    assessment_type TEXT NOT NULL,
    max_score REAL NOT NULL CHECK(max_score > 0),
    score REAL NOT NULL CHECK(score BETWEEN 0 AND max_score),
    FOREIGN KEY(enrollment_id) REFERENCES enrollments(enrollment_id) ON DELETE CASCADE
);
