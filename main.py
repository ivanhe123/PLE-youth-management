import streamlit as st
import streamlit.components.v1 as components
from st_keyup import st_keyup  # Using the streamlit-keyup library

st.title("Teacher Enrollment Forum")

# Extended teacher data with the new fields
teacher_data = [
    {
        "class_name": "Physics 101",
        "teacher": "John Doe",
        "course_description": "This course introduces the fundamentals of physics with a focus on motion, energy, and interactive experiments.",
        "teacher_description": "John brings over 10 years of experience, making complex scientific ideas both accessible and engaging.",
        "subject": "Physics",
        "grade": "High School"
    },
    {
        "class_name": "Algebra Basics",
        "teacher": "Jane Smith",
        "course_description": "An engaging introduction to algebra concepts with a strong emphasis on problem-solving and real-life applications.",
        "teacher_description": "Jane is celebrated for her interactive lessons and her deep understanding of algebra, making the subject fun and relatable.",
        "subject": "Mathematics",
        "grade": "Middle School"
    },
    {
        "class_name": "Creative Art",
        "teacher": "Emily Johnson",
        "course_description": "Explore various art techniques and expressions in this creativity-focused class.",
        "teacher_description": "Emily is passionate about nurturing artistic talents and encouraging self-expression in every student.",
        "subject": "Art",
        "grade": "Elementary"
    },
    {
        "class_name": "Advanced Chemistry",
        "teacher": "Michael Brown",
        "course_description": "A deep dive into chemical reactions and experiments designed to challenge and inspire future scientists.",
        "teacher_description": "Michael, a specialist in chemistry, has a knack for turning complex concepts into engaging experiments.",
        "subject": "Chemistry",
        "grade": "High School"
    },
]

def display_card(teacher):
    """
    This function displays a teacher card with:
      - Class Name (prominent)
      - Teacher Name
      - Grade and Subject
      - Course Description
      - Teacher Description
    """
    class_name = teacher["class_name"]
    teacher_name = teacher["teacher"]
    course_description = teacher["course_description"]
    teacher_description = teacher["teacher_description"]
    subject = teacher["subject"]
    grade = teacher["grade"]

    card_html = f"""
    <div style="background-color:#d3d3d3; padding:20px; border-radius:10px; margin-bottom:15px;">
        <!-- Class Name (most prominent) -->
        <h2 style="margin-bottom: 10px;">{class_name}</h2>
        <!-- Teacher name -->
        <h4 style="margin: 0;">Teacher: {teacher_name}</h4>
        <!-- Grade & Subject -->
        <p style="margin: 5px 0;"><b>Grade:</b> {grade} | <b>Subject:</b> {subject}</p>
        <!-- Course Description -->
        <p style="margin-bottom: 10px;"><b>Course Description:</b> {course_description}</p>
        <!-- Teacher Description -->
        <p><b>Teacher Description:</b> {teacher_description}</p>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# --- Create a keyup-enabled search bar ---
# The widget updates st.session_state['teacher_search'] as the user types.
search_query = st_keyup(
    "Search classes, teachers, or descriptions",
    key="teacher_search",
    placeholder="Type a keyword..."
)

# --- Create subject and grade dropdown filters ---
# Add an "All" option to disable filtering.
subject_options = ["All"] + sorted({t["subject"] for t in teacher_data})
grade_options = ["All"] + sorted({t["grade"] for t in teacher_data})

subject_filter = st.selectbox("Filter by Subject", options=subject_options, index=0)
grade_filter = st.selectbox("Filter by Grade", options=grade_options, index=0)

# --- Filtering teacher data based on search, subject, and grade ---
filtered_data = teacher_data

if search_query:
    lower_query = search_query.lower()
    filtered_data = [
        t for t in filtered_data
        if (lower_query in t["class_name"].lower() or
            lower_query in t["teacher"].lower() or
            lower_query in t["course_description"].lower() or
            lower_query in t["teacher_description"].lower() or
            lower_query in t["subject"].lower() or
            lower_query in t["grade"].lower())
    ]

if subject_filter != "All":
    filtered_data = [t for t in filtered_data if t["subject"] == subject_filter]

if grade_filter != "All":
    filtered_data = [t for t in filtered_data if t["grade"] == grade_filter]

# --- Display the teacher cards based on the filtered data ---
if filtered_data:
    for teacher in filtered_data:
        display_card(teacher)
else:
    st.write("No classes found matching your filters.")
