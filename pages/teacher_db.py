# teacher_db.py

import sqlite3

DB_FILE = "teacher.db"


def init_teacher_db():
    """
    Initialize the teacher database and create the teachers table if it doesn't exist.
    The table structure includes:
      - id: Primary Key
      - teacher_name: Unique teacher name
      - passcode: The teacher's passcode
      - teacher_description: Profile description for the teacher
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_name TEXT NOT NULL UNIQUE,
            passcode TEXT NOT NULL,
            teacher_description TEXT
        )
    ''')
    conn.commit()
    conn.close()


def add_teacher(teacher_name, passcode, teacher_description=""):
    """
    Add a new teacher account to the database.

    Parameters:
      teacher_name (str): The name of the teacher.
      passcode (str): The teacher's passcode.
      teacher_description (str): An optional description of the teacher.
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO teachers (teacher_name, passcode, teacher_description) VALUES (?, ?, ?)",
            (teacher_name, passcode, teacher_description)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Teacher '{teacher_name}' already exists.")
    finally:
        conn.close()


def get_all_teachers():
    """
    Retrieve all teacher records from the database.

    Returns:
      List of tuples, each in the form: (id, teacher_name, passcode, teacher_description)
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM teachers")
    teachers = cur.fetchall()
    conn.close()
    return teachers


def get_teacher(teacher_name):
    """
    Retrieve a single teacher record by teacher name.

    Parameters:
      teacher_name (str): The name of the teacher.

    Returns:
      A tuple of the form (id, teacher_name, passcode, teacher_description) or None if not found.
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM teachers WHERE teacher_name=?", (teacher_name,))
    teacher = cur.fetchone()  # (id, teacher_name, passcode, teacher_description)
    conn.close()
    return teacher


def update_teacher_description(teacher_name, teacher_description):
    """
    Update the teacher's description only.

    Parameters:
      teacher_name (str): The teacher's name.
      teacher_description (str): The updated description.
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "UPDATE teachers SET teacher_description=? WHERE teacher_name=?",
        (teacher_description, teacher_name)
    )
    conn.commit()
    conn.close()


def update_teacher_credentials(teacher_name, new_passcode, new_teacher_description):
    """
    Update a teacher's passcode and their profile description.

    Parameters:
      teacher_name (str): The teacher's name.
      new_passcode (str): The new passcode.
      new_teacher_description (str): The new teacher description.
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "UPDATE teachers SET passcode=?, teacher_description=? WHERE teacher_name=?",
        (new_passcode, new_teacher_description, teacher_name)
    )
    conn.commit()
    conn.close()


def delete_teacher(teacher_name):
    """
    Delete a teacher record from the database by teacher name.

    Parameters:
      teacher_name (str): The teacher's name.
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM teachers WHERE teacher_name=?", (teacher_name,))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_teacher_db()
    # Uncomment the following lines to test adding and retrieving teachers:
    # add_teacher("John Doe", "password123", "An experienced Physics teacher.")
    # add_teacher("Jane Smith", "pass123", "A passionate Mathematics educator.")
    # print(get_all_teachers())
