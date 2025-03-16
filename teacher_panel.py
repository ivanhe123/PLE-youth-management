# teacher_panel.py

import streamlit as st
import json
from teacher_db import init_teacher_db, get_teacher, update_teacher_description
from courses_db import init_courses_db, add_course, get_courses_by_teacher, update_course, delete_course

st.set_page_config(page_title="Teacher Panel", layout="wide")
st.title("Teacher Panel")

# Initialize both databases.
init_teacher_db()
init_courses_db()
st.experimental_rerun = st.rerun
# ---------------------------
# TEACHER LOGIN SECTION
# ---------------------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.subheader("Teacher Login")
    with st.form("login_form"):
        teacher_name_input = st.text_input("Teacher Name")
        teacher_passcode_input = st.text_input("Passcode", type="password")
        login_button = st.form_submit_button("Login")
    if login_button:
        teacher_record = get_teacher(teacher_name_input)
        # Expected teacher_record: (id, teacher_name, passcode, teacher_description)
        if teacher_record and teacher_record[2] == teacher_passcode_input:
            st.session_state["logged_in"] = True
            st.session_state["teacher_name"] = teacher_record[1]
            st.session_state["teacher_description"] = teacher_record[3] if teacher_record[3] is not None else ""
            st.session_state["teacher_passcode"] = teacher_passcode_input
            st.success(f"Logged in as {teacher_record[1]}")
        else:
            st.error("Invalid name or passcode. Please try again.")
else:
    # ---------------------------
    # TEACHER PANEL ACTIONS
    # ---------------------------
    st.sidebar.header(f"Welcome, {st.session_state['teacher_name']}!")
    if st.sidebar.button("Logout"):
        for key in ["logged_in", "teacher_name", "teacher_description", "teacher_passcode"]:
            if key in st.session_state:
                del st.session_state[key]
        st.experimental_rerun()

    teacher_action = st.sidebar.radio("Teacher Actions", ("View My Courses", "Create Course", "Edit Profile"))

    # -----------------------------------
    # (1) View My Courses Section
    # -----------------------------------
    if teacher_action == "View My Courses":
        st.subheader("My Courses")
        search_query = st.text_input("Search Your Courses", placeholder="Enter keyword to filter your courses")

        # Fetch courses created by the logged-in teacher.
        my_courses = get_courses_by_teacher(st.session_state["teacher_name"])

        # Filter courses using search query.
        if search_query:
            filtered_courses = []
            query = search_query.lower()
            for course in my_courses:
                # Course record:
                # (id, class_name, teacher, subject, grade, course_description, teacher_description, max_students, enrolled_students)
                if (query in course[1].lower() or query in course[3].lower() or
                        query in course[4].lower() or query in course[5].lower() or
                        query in course[6].lower()):
                    filtered_courses.append(course)
        else:
            filtered_courses = my_courses

        if filtered_courses:
            for course in filtered_courses:
                (course_id, class_name, teacher, subject, grade, course_desc, teacher_desc,
                 max_students, enrolled_students) = course
                # Parse enrolled_students field (JSON string) into a Python list.
                try:
                    enrolled_list = json.loads(enrolled_students)
                except Exception:
                    enrolled_list = []
                num_enrolled = len(enrolled_list)

                with st.container():
                    st.markdown(f"### {class_name}")
                    st.markdown(
                        f"**Subject:** {subject}  |  **Grade:** {grade}  |  **Max Students:** {max_students}  |  **Enrolled:** {num_enrolled}"
                    )
                    st.markdown(f"**Course Description:** {course_desc}")
                    st.markdown(f"**Teacher Description:** {teacher_desc}")

                    if enrolled_list:
                        with st.expander("View Enrolled Students"):
                            for stud in enrolled_list:
                                st.write(stud)

                    col1, col2 = st.columns(2)
                    if col1.button("Edit", key=f"edit_{course_id}"):
                        st.session_state["editing_course"] = course_id
                    if col2.button("Delete", key=f"delete_{course_id}"):
                        delete_course(course_id)
                        st.success(f"Course '{class_name}' deleted successfully.")
                        st.experimental_rerun()

                    # Inline edit form for this course.
                    if "editing_course" in st.session_state and st.session_state["editing_course"] == course_id:
                        st.markdown("#### Edit Course")
                        with st.form(key=f"edit_course_form_{course_id}"):
                            new_class_name = st.text_input("Class Name", value=class_name)
                            new_subject = st.text_input("Subject", value=subject)
                            new_grade = st.text_input("Grade", value=grade)
                            new_course_desc = st.text_area("Course Description", value=course_desc)
                            new_teacher_desc = st.text_area("Teacher Description", value=teacher_desc)
                            new_max_students = st.number_input("Max Students", value=int(max_students), min_value=1)
                            update_btn = st.form_submit_button("Update Course")
                        if update_btn:
                            # Pass along the existing enrolled_students unchanged.
                            update_course(
                                course_id,
                                new_class_name,
                                st.session_state["teacher_name"],
                                new_subject,
                                new_grade,
                                new_course_desc,
                                new_teacher_desc,
                                new_max_students,
                                enrolled_students  # Keep current enrolled_students JSON string.
                            )
                            st.success("Course updated successfully!")
                            del st.session_state["editing_course"]
                            st.experimental_rerun()
                        if st.button("Cancel Edit", key=f"cancel_edit_{course_id}"):
                            del st.session_state["editing_course"]
                            st.experimental_rerun()
                        st.markdown("---")
        else:
            st.info("No courses found matching your criteria.")

    # -----------------------------------
    # (2) Create Course Section
    # -----------------------------------
    elif teacher_action == "Create Course":
        st.subheader("Create New Course")
        with st.form("create_course_form"):
            course_name = st.text_input("Course Name")
            course_subject = st.text_input("Subject")
            course_grade = st.text_input("Grade")
            course_description = st.text_area("Course Description")
            # Teacher Description is taken from teacher profile.
            st.markdown("Teacher Description (from your profile) will be attached automatically.")
            max_students = st.number_input("Max Students", value=2, min_value=1)
            submit_course = st.form_submit_button("Create Course")
        if submit_course:
            add_course(
                class_name=course_name,
                teacher=st.session_state["teacher_name"],
                subject=course_subject,
                grade=course_grade,
                course_description=course_description,
                teacher_description=st.session_state["teacher_description"],
                max_students=max_students,
                enrolled_students="[]"  # New course has an empty enrolled list.
            )
            st.success("Course created successfully!")
            st.experimental_rerun()

    # -----------------------------------
    # (3) Edit Profile Section
    # -----------------------------------
    elif teacher_action == "Edit Profile":
        st.subheader("Edit Teacher Profile")
        with st.form("edit_profile_form"):
            new_teacher_description = st.text_area("Teacher Description", value=st.session_state["teacher_description"])
            update_profile = st.form_submit_button("Update Profile")
        if update_profile:
            update_teacher_description(st.session_state["teacher_name"], new_teacher_description)
            st.session_state["teacher_description"] = new_teacher_description
            st.success("Profile updated successfully!")
            st.experimental_rerun()
