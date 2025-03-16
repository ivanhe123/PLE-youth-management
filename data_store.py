# data_store.py

import json
import os

DATA_FILE = "teacher_data.json"

def load_teacher_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        # Initialize default data if the file doesn't exist
        data = [
            {
                "class_name": "Physics 101",
                "teacher": "John Doe",
                "course_description": "This course introduces the fundamentals of physics with a focus on motion, energy, and hands-on experiments.",
                "teacher_description": "John brings over 10 years of experience in making complex scientific ideas accessible and engaging.",
                "subject": "Physics",
                "grade": "High School",
                "password": "password123"
            },
            {
                "class_name": "Algebra Basics",
                "teacher": "Jane Smith",
                "course_description": "An engaging introduction to algebra with applications in real-life problem solving.",
                "teacher_description": "Jane is celebrated for her interactive lessons and passion for cultivating problem-solving skills.",
                "subject": "Mathematics",
                "grade": "Middle School",
                "password": "pass123"
            },
            {
                "class_name": "Creative Art",
                "teacher": "Emily Johnson",
                "course_description": "Explore various art techniques and creative expression in this hands-on course.",
                "teacher_description": "Emily inspires creativity through innovative projects and gentle guidance.",
                "subject": "Art",
                "grade": "Elementary",
                "password": "artpass"
            },
            {
                "class_name": "Advanced Chemistry",
                "teacher": "Michael Brown",
                "course_description": "A dive into chemical reactions and complex experiments designed for the curious mind.",
                "teacher_description": "Michael turns complex chemistry concepts into engaging experiments.",
                "subject": "Chemistry",
                "grade": "High School",
                "password": "chem123"
            }
        ]
        save_teacher_data(data)
        return data

def save_teacher_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)
