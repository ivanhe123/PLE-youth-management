# enrollment_forum.py

import streamlit as st
import json
from courses_db import init_courses_db, get_all_courses, update_course

st.set_page_config(page_title="Enrollment Forum", layout="wide")
st.title("Enrollment Forum")

# Initialize (or ensure) the courses database is ready.
init_courses_db()
st.experimental_rerun=st.rerun
# ---------------------------
# Search and Filter Courses
# ---------------------------
search_query = st.text_input("Search Courses", placeholder="Enter keyword to filter courses")

all_courses = get_all_courses()
# Each course record is assumed to have the following schema:
# (id, class_name, teacher, subject, grade, course_description, teacher_description, max_students, enrolled_students)

if search_query:
    filtered_courses = []
    q = search_query.lower()
    for course in all_courses:
        if (q in course[1].lower() or q in course[2].lower() or q in course[3].lower() or
            q in course[4].lower() or q in course[5].lower() or q in course[6].lower()):
            filtered_courses.append(course)
else:
    filtered_courses = all_courses

# ---------------------------
# Display Each Course Card
# ---------------------------
for course in filtered_courses:
    (course_id, class_name, teacher, subject, grade, course_desc, teacher_desc,
     max_students, enrolled_students) = course

    # Ensure enrolled_students is parsed as a Python list from its JSON string.
    try:
        enrolled_list = json.loads(enrolled_students)
    except Exception:
        enrolled_list = []

    num_enrolled = len(enrolled_list)

    st.markdown(f"## {class_name}")
    st.markdown(f"**Teacher:** {teacher} | **Subject:** {subject} | **Grade:** {grade}")
    st.markdown(f"**Course Description:** {course_desc}")
    st.markdown(f"**Teacher Description:** {teacher_desc}")
    st.markdown(f"**Max Students:** {max_students} | **Enrolled:** {num_enrolled}")

    # ---------------------------------------
    # Enrollment Button with Threshold Check
    # ---------------------------------------
    if num_enrolled >= max_students:
        st.button("Enroll", key=f"enroll_{course_id}", disabled=True)
        st.info("Course enrollment is full.")
    else:
        if st.button("Enroll", key=f"enroll_{course_id}"):
            # Store the course ID in session state to trigger enrollment form.
            st.session_state["enroll_course_id"] = course_id
            st.experimental_rerun()

    # ---------------------------------------
    # Enrollment Form (only for the selected course)
    # ---------------------------------------
    if "enroll_course_id" in st.session_state and st.session_state["enroll_course_id"] == course_id:
        st.markdown("### Enrollment Form")
        with st.form(key=f"enroll_form_{course_id}"):
            student_name = st.text_input("Enter Your Name")
            enroll_submit = st.form_submit_button("Submit Enrollment")
        if enroll_submit:
            if student_name.strip() != "":
                enrolled_list.append(student_name.strip())
                # Update the enrolled_students field in the database.
                new_enrolled_json = json.dumps(enrolled_list)
                update_course(
                    course_id,
                    class_name,
                    teacher,
                    subject,
                    grade,
                    course_desc,
                    teacher_desc,
                    max_students,
                    new_enrolled_json
                )
                st.success(f"{student_name} has been enrolled successfully!")
                del st.session_state["enroll_course_id"]
                st.experimental_rerun()
            else:
                st.error("Please enter your name to enroll.")
        if st.button("Cancel Enrollment", key=f"cancel_enroll_{course_id}"):
            del st.session_state["enroll_course_id"]
            st.experimental_rerun()

    # ---------------------------------------
    # Expandable Section for Enrolled Students
    # ---------------------------------------
    with st.expander("View Enrolled Students"):
        if enrolled_list:
            for student in enrolled_list:
                st.write(student)
        else:
            st.write("No students enrolled yet.")

    st.markdown("---")
