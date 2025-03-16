# courses_db.py

import sqlite3

DB_FILE = "courses.db"

def init_courses_db():
    """
    Initialize the courses database and create the courses table with the new schema.
    If the existing table does not have the required columns (max_students and enrolled_students),
    drop it and re-create it.
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Check if the courses table exists and retrieve its columns
    cur.execute("PRAGMA table_info(courses)")
    columns = cur.fetchall()  # Each row: (cid, name, type, notnull, dflt_value, pk)

    if len(columns) < 9:
        # If there are fewer than 9 columns, drop the table to avoid schema mismatch.
        cur.execute("DROP TABLE IF EXISTS courses")
        conn.commit()

    # Create the courses table with the new schema.
    cur.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT NOT NULL,
            teacher TEXT NOT NULL,
            subject TEXT,
            grade TEXT,
            course_description TEXT,
            teacher_description TEXT,
            max_students INTEGER DEFAULT 2,
            enrolled_students TEXT DEFAULT '[]'
        )
    ''')
    conn.commit()
    conn.close()

def add_course(class_name, teacher, subject, grade, course_description, teacher_description, max_students=2, enrolled_students="[]"):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO courses 
        (class_name, teacher, subject, grade, course_description, teacher_description, max_students, enrolled_students)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (class_name, teacher, subject, grade, course_description, teacher_description, max_students, enrolled_students)
    )
    conn.commit()
    conn.close()

def get_all_courses():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM courses")
    courses = cur.fetchall()
    conn.close()
    return courses

def get_course_by_id(course_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM courses WHERE id=?", (course_id,))
    course = cur.fetchone()
    conn.close()
    return course

def update_course(course_id, class_name, teacher, subject, grade, course_description, teacher_description, max_students, enrolled_students):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE courses 
        SET class_name=?, teacher=?, subject=?, grade=?, course_description=?, teacher_description=?, max_students=?, enrolled_students=?
        WHERE id=?
        """,
        (class_name, teacher, subject, grade, course_description, teacher_description, max_students, enrolled_students, course_id)
    )
    conn.commit()
    conn.close()

def delete_course(course_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM courses WHERE id=?", (course_id,))
    conn.commit()
    conn.close()

def get_courses_by_teacher(teacher):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM courses WHERE teacher=?", (teacher,))
    courses = cur.fetchall()
    conn.close()
    return courses

if __name__ == "__main__":
    init_courses_db()
    # Optionally, add a sample course once.
    # add_course("Physics 101", "John Doe", "Physics", "High School", "Basics of motion and energy.", "Experienced teacher", 2, "[]")
    courses = get_all_courses()
    print("Courses:", courses)
