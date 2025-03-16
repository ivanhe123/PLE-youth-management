import streamlit as st
import json
from teacher_db import (
    init_teacher_db,
    get_all_teachers,
    update_teacher_credentials,  # Updates both passcode and teacher description.
    add_teacher,
)
from courses_db import (
    init_courses_db,
    get_all_courses,
    update_course,
    delete_course,
    add_course,
)
st.experimental_rerun = st.rerun
st.set_page_config(page_title="Admin Panel", layout="wide")
st.title("Admin Panel")

# Initialize both databases.
init_teacher_db()
init_courses_db()

# ---------------------------
# ADMIN LOGIN SECTION
# ---------------------------
if "admin_logged_in" not in st.session_state:
    st.session_state["admin_logged_in"] = False

if not st.session_state["admin_logged_in"]:
    st.subheader("Admin Login")
    admin_passcode = st.text_input("Enter Admin Passcode", type="password")
    if st.button("Login"):
        if admin_passcode == "1234":
            st.session_state["admin_logged_in"] = True
            st.success("Admin login successful!")
        else:
            st.error("Invalid passcode! Please try again.")

# ---------------------------
# MAIN ADMIN FUNCTIONALITIES
# ---------------------------
if st.session_state.get("admin_logged_in"):

    # Sidebar: choose admin mode.
    admin_mode = st.sidebar.radio("Admin Options", ["Impersonate Teacher", "Manage Courses"])

    # ==============================================
    # 1. IMPERSONATE TEACHER (Manage Teacher Profiles)
    # ==============================================
    if admin_mode == "Impersonate Teacher":
        st.header("Teacher Impersonation")
        # If already impersonating a teacher, show teacher panel.
        if "impersonated_teacher" in st.session_state:
            teacher_name = st.session_state["impersonated_teacher"]
            teacher_pass = st.session_state["impersonated_teacher_pass"]
            teacher_desc = st.session_state.get("impersonated_teacher_description", "")
            st.info(f"Currently impersonating teacher: **{teacher_name}**")
            st.write(f"**Passcode:** {teacher_pass}")
            if st.button("Return to Admin"):
                for key in ["impersonated_teacher", "impersonated_teacher_pass", "impersonated_teacher_description"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.experimental_rerun()

            # Impersonated teacher panel functionalities (similar to teacher panel)
            teacher_action = st.radio("Teacher Actions", ("View My Courses", "Create Course", "Edit Profile"))

            # (a) View My Courses
            if teacher_action == "View My Courses":
                st.subheader("My Courses")
                search_query = st.text_input("Search Your Courses", placeholder="Enter keyword...",
                                             key="teacher_search")
                # Get courses for this teacher.
                all_courses = get_all_courses()
                my_courses = [course for course in all_courses if course[2] == teacher_name]
                if search_query:
                    filtered_courses = []
                    q = search_query.lower()
                    for course in my_courses:
                        # course record: (id, class_name, teacher, subject, grade, course_desc, teacher_desc, max_students, enrolled_students)
                        if (q in course[1].lower() or q in course[3].lower() or
                                q in course[4].lower() or q in course[5].lower() or
                                q in course[6].lower()):
                            filtered_courses.append(course)
                    display_courses = filtered_courses
                else:
                    display_courses = my_courses

                if display_courses:
                    for course in display_courses:
                        (course_id, class_name, teacher, subject, grade,
                         course_desc, teacher_desc, max_students, enrolled_students) = course
                        try:
                            enrolled_list = json.loads(enrolled_students)
                        except Exception:
                            enrolled_list = []
                        num_enrolled = len(enrolled_list)
                        with st.container():
                            st.markdown(f"### {class_name}")
                            st.markdown(
                                f"**Subject:** {subject} | **Grade:** {grade} | **Max Students:** {max_students} | **Enrolled:** {num_enrolled}")
                            st.markdown(f"**Course Description:** {course_desc}")
                            st.markdown(f"**Teacher Description:** {teacher_desc}")
                            with st.expander("View Enrolled Students"):
                                if enrolled_list:
                                    for s in enrolled_list:
                                        st.write(s)
                                else:
                                    st.write("No students enrolled.")
                            col1, col2 = st.columns(2)
                            if col1.button("Edit", key=f"t_edit_{course_id}"):
                                st.session_state["t_editing_course"] = course_id
                            if col2.button("Delete", key=f"t_delete_{course_id}"):
                                delete_course(course_id)
                                st.success(f"Course '{class_name}' deleted.")
                                st.experimental_rerun()

                            if "t_editing_course" in st.session_state and st.session_state[
                                "t_editing_course"] == course_id:
                                st.markdown("#### Edit Course")
                                with st.form(key=f"t_edit_form_{course_id}"):
                                    new_class_name = st.text_input("Class Name", value=class_name)
                                    new_subject = st.text_input("Subject", value=subject)
                                    new_grade = st.text_input("Grade", value=grade)
                                    new_course_desc = st.text_area("Course Description", value=course_desc)
                                    new_teacher_desc = st.text_area("Teacher Description", value=teacher_desc)
                                    new_max_students = st.number_input("Max Students", value=int(max_students),
                                                                       min_value=1)
                                    update_btn = st.form_submit_button("Update Course")
                                if update_btn:
                                    update_course(
                                        course_id,
                                        new_class_name,
                                        teacher_name,
                                        new_subject,
                                        new_grade,
                                        new_course_desc,
                                        new_teacher_desc,
                                        new_max_students,
                                        json.dumps(enrolled_list)
                                    )
                                    st.success("Course updated successfully!")
                                    del st.session_state["t_editing_course"]
                                    st.experimental_rerun()
                                if st.button("Cancel Edit", key=f"t_cancel_edit_{course_id}"):
                                    del st.session_state["t_editing_course"]
                                    st.experimental_rerun()
                                st.markdown("---")
                else:
                    st.info("No courses found for this teacher.")

            # (b) Create Course
            elif teacher_action == "Create Course":
                st.subheader("Create New Course")
                with st.form("teacher_create_course_form"):
                    course_name = st.text_input("Course Name")
                    subject = st.text_input("Subject")
                    grade = st.text_input("Grade")
                    course_desc = st.text_area("Course Description")
                    st.markdown("Teacher Description (from your profile) will be attached automatically.")
                    max_students = st.number_input("Max Students", value=2, min_value=1)
                    submit_course = st.form_submit_button("Create Course")
                if submit_course:
                    add_course(
                        class_name=course_name,
                        teacher=teacher_name,
                        subject=subject,
                        grade=grade,
                        course_description=course_desc,
                        teacher_description=teacher_desc,
                        max_students=max_students,
                        enrolled_students="[]"
                    )
                    st.success("Course created successfully!")
                    st.experimental_rerun()

            # (c) Edit Profile
            elif teacher_action == "Edit Profile":
                st.subheader("Edit Teacher Profile")
                with st.form("teacher_edit_profile_form"):
                    new_teacher_pass = st.text_input("Teacher Passcode", value=teacher_pass)
                    new_teacher_desc = st.text_area("Teacher Description", value=teacher_desc)
                    update_profile = st.form_submit_button("Update Profile")
                if update_profile:
                    # Update both passcode and description.
                    update_teacher_credentials(teacher_name, new_teacher_pass, new_teacher_desc)
                    st.session_state["impersonated_teacher_pass"] = new_teacher_pass
                    st.session_state["impersonated_teacher_description"] = new_teacher_desc
                    st.success("Profile updated successfully!")
                    st.experimental_rerun()

        # If not impersonating, show search for teacher to impersonate.
        else:
            st.subheader("Search for a Teacher to Impersonate")
            search_teacher_input = st.text_input("Search Teachers", placeholder="Enter teacher name...")
            teacher_profiles = get_all_teachers()
            if search_teacher_input:
                filtered_teachers = [t for t in teacher_profiles if search_teacher_input.lower() in t[1].lower()]
            else:
                filtered_teachers = teacher_profiles

            if filtered_teachers:
                for teacher in filtered_teachers:
                    tid, tname, tpass, tdesc = teacher
                    with st.container():
                        st.markdown(f"#### {tname}")
                        st.markdown(f"**Description:** {tdesc if tdesc else 'N/A'}")
                        st.markdown(f"**Passcode:** {tpass}")
                        if st.button("Login As", key=f"login_as_{tid}"):
                            st.session_state["impersonated_teacher"] = tname
                            st.session_state["impersonated_teacher_pass"] = tpass
                            st.session_state["impersonated_teacher_description"] = tdesc if tdesc else ""
                            st.experimental_rerun()
                    st.markdown("---")
            else:
                st.info("No teacher profiles found.")

            st.markdown("---")
            st.subheader("Add New Teacher Profile")
            with st.form("add_teacher_form"):
                new_teacher_name = st.text_input("Teacher Name")
                new_teacher_pass = st.text_input("Teacher Passcode", type="password")
                new_teacher_desc = st.text_area("Teacher Description")
                add_teacher_btn = st.form_submit_button("Add Teacher Profile")
            if add_teacher_btn:
                if new_teacher_name and new_teacher_pass:
                    try:
                        add_teacher(new_teacher_name, new_teacher_pass, new_teacher_desc)
                        st.success("New teacher profile added!")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error adding teacher: {e}")
                else:
                    st.error("Teacher Name and Teacher Passcode are required.")

    # ============================
    # 2. MANAGE COURSES (Admin Mode)
    # ============================
    elif admin_mode == "Manage Courses":
        st.header("Manage All Courses")
        search_course = st.text_input("Search Courses", placeholder="Enter keyword...", key="admin_search_course")
        all_courses = get_all_courses()
        if search_course:
            filtered_courses = []
            q = search_course.lower()
            for course in all_courses:
                if (q in course[1].lower() or q in course[2].lower() or
                        q in course[3].lower() or q in course[4].lower() or
                        q in course[5].lower() or q in course[6].lower()):
                    filtered_courses.append(course)
        else:
            filtered_courses = all_courses

        if filtered_courses:
            for course in filtered_courses:
                (course_id, class_name, teacher, subject, grade,
                 course_desc, teacher_desc, max_students, enrolled_students) = course
                try:
                    enrolled_list = json.loads(enrolled_students)
                except Exception:
                    enrolled_list = []
                num_enrolled = len(enrolled_list)
                with st.container():
                    st.markdown(f"### {class_name}")
                    st.markdown(f"**Teacher:** {teacher} | **Subject:** {subject} | **Grade:** {grade}")
                    st.markdown(f"**Course Description:** {course_desc}")
                    st.markdown(f"**Teacher Description:** {teacher_desc}")
                    st.markdown(f"**Max Students:** {max_students} | **Enrolled:** {num_enrolled}")
                    with st.expander("View Enrolled Students"):
                        if enrolled_list:
                            for s in enrolled_list:
                                st.write(s)
                        else:
                            st.write("No students enrolled yet.")

                    col1, col2, col3, col4 = st.columns(4)
                    if col1.button("Edit", key=f"admin_edit_{course_id}"):
                        st.session_state["admin_editing_course"] = course_id
                    if col2.button("Delete", key=f"admin_delete_{course_id}"):
                        delete_course(course_id)
                        st.success(f"Course '{class_name}' deleted successfully.")
                        st.experimental_rerun()
                    if col3.button("Edit Enrollments", key=f"admin_edit_enrollment_{course_id}"):
                        st.session_state["admin_editing_enrollment"] = course_id
                    if col4.button("Cancel Enrollment Edit", key=f"admin_cancel_enrollment_{course_id}"):
                        if "admin_editing_enrollment" in st.session_state and st.session_state[
                            "admin_editing_enrollment"] == course_id:
                            del st.session_state["admin_editing_enrollment"]
                            st.experimental_rerun()

                    if "admin_editing_enrollment" in st.session_state and st.session_state[
                        "admin_editing_enrollment"] == course_id:
                        st.markdown("#### Edit Enrollments")
                        for idx, student in enumerate(enrolled_list):
                            colA, colB = st.columns([3, 1])
                            colA.write(student)
                            if colB.button("Remove", key=f"admin_remove_{course_id}_{idx}"):
                                removed = enrolled_list.pop(idx)
                                new_enrolled_json = json.dumps(enrolled_list)
                                update_course(course_id, class_name, teacher, subject, grade, course_desc, teacher_desc,
                                              max_students, new_enrolled_json)
                                st.success(f"Student '{removed}' removed.")
                                st.experimental_rerun()
                        with st.form(key=f"admin_add_student_form_{course_id}"):
                            new_student = st.text_input("New Student Name")
                            add_student_btn = st.form_submit_button("Enroll Student")
                        if add_student_btn:
                            if new_student.strip() != "":
                                if len(enrolled_list) < max_students:
                                    enrolled_list.append(new_student.strip())
                                    new_enrolled_json = json.dumps(enrolled_list)
                                    update_course(course_id, class_name, teacher, subject, grade, course_desc,
                                                  teacher_desc, max_students, new_enrolled_json)
                                    st.success(f"Student '{new_student}' enrolled.")
                                    st.experimental_rerun()
                                else:
                                    st.error("Cannot enroll student. Course is full.")
                            else:
                                st.error("Please enter a valid student name.")
                        if st.button("Finish Editing Enrollments", key=f"admin_finish_edit_{course_id}"):
                            if "admin_editing_enrollment" in st.session_state:
                                del st.session_state["admin_editing_enrollment"]
                                st.experimental_rerun()

                    if "admin_editing_course" in st.session_state and st.session_state[
                        "admin_editing_course"] == course_id:
                        st.markdown("#### Edit Course")
                        with st.form(key=f"admin_edit_course_form_{course_id}"):
                            new_class_name = st.text_input("Class Name", value=class_name)
                            new_teacher = st.text_input("Teacher", value=teacher)
                            new_subject = st.text_input("Subject", value=subject)
                            new_grade = st.text_input("Grade", value=grade)
                            new_course_desc = st.text_area("Course Description", value=course_desc)
                            new_teacher_desc = st.text_area("Teacher Description", value=teacher_desc)
                            new_max_students = st.number_input("Max Students", value=int(max_students), min_value=1)
                            update_btn = st.form_submit_button("Update Course")
                        if update_btn:
                            update_course(course_id, new_class_name, new_teacher, new_subject, new_grade,
                                          new_course_desc, new_teacher_desc, new_max_students,
                                          json.dumps(enrolled_list))
                            st.success("Course updated successfully!")
                            del st.session_state["admin_editing_course"]
                            st.experimental_rerun()
                        if st.button("Cancel Edit", key=f"admin_cancel_edit_{course_id}"):
                            del st.session_state["admin_editing_course"]
                            st.experimental_rerun()
                        st.markdown("---")
        else:
            st.info("No courses found matching your search criteria.")
