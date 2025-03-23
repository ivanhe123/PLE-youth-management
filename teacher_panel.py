# teacher_panel.py

import streamlit as st
import json
from teacher_db import init_teacher_db, get_teacher, update_teacher_description
from courses_db import init_courses_db, add_course, get_courses_by_teacher, update_course, delete_course
# Store selected language in session state
if "selected_language" not in st.session_state:
    st.session_state.selected_language = "English (英语)"
st.experimental_rerun = st.rerun
lang_options = ["English (英语)", "中文 (Chinese)"]
selected_language = st.sidebar.selectbox("Select Language/选择语言", lang_options)
st.session_state.selected_language = selected_language
lang = st.session_state.get("selected_language", "English (英语)")
if lang == "中文 (Chinese)":
    # teacher_panel.py

    import streamlit as st
    import json
    from teacher_db import init_teacher_db, get_teacher, update_teacher_description
    from courses_db import init_courses_db, add_course, get_courses_by_teacher, update_course, delete_course

    st.title("老师面板")

    # Initialize both databases.
    init_teacher_db()
    init_courses_db()

    # ---------------------------
    # TEACHER LOGIN SECTION
    # ---------------------------
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        st.subheader("老师登入")
        with st.form("login_form"):
            teacher_name_input = st.text_input("老师名")
            teacher_passcode_input = st.text_input("密码", type="password")
            login_button = st.form_submit_button("登入")
        if login_button:
            teacher_record = get_teacher(teacher_name_input)
            # Expected teacher_record: (id, teacher_name, passcode, teacher_description)
            if teacher_record and teacher_record[2] == teacher_passcode_input:
                st.session_state["logged_in"] = True
                st.session_state["teacher_name"] = teacher_record[1]
                st.session_state["teacher_description"] = teacher_record[3] if teacher_record[3] is not None else ""
                st.session_state["teacher_passcode"] = teacher_passcode_input
                st.success(f"以{teacher_record[1]}身份登入！")
            else:
                st.error("登入失败！")
    else:
        # ---------------------------
        # TEACHER PANEL ACTIONS
        # ---------------------------
        st.sidebar.header(f"欢迎, {st.session_state['teacher_name']}!")
        if st.sidebar.button("登出"):
            for key in ["logged_in", "teacher_name", "teacher_description", "teacher_passcode"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.experimental_rerun()

        teacher_action = st.sidebar.radio("老师选项", ("我的课程", "创建课程", "编辑个人信息"))

        # -----------------------------------
        # (1) View My Courses Section
        # -----------------------------------
        if teacher_action == "我的课程":
            st.subheader("我的课程")
            search_query = st.text_input("搜索我的课程", placeholder="输入任意关键词（课程名，科目，年级，简介）")

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
                            f"**科目:** {subject}  |  **年级:** {grade}  |  **最多可报名人数:** {max_students}  |  **已报名人数:** {num_enrolled}"
                        )
                        st.markdown(f"**课程简介:** {course_desc}")
                        st.markdown(f"**老师简介:** {teacher_desc}")

                        if enrolled_list:
                            with st.expander("以报名的学生"):
                                for stud in enrolled_list:
                                    st.write(stud)

                        col1, col2 = st.columns(2)
                        if col1.button("编辑", key=f"edit_{course_id}"):
                            st.session_state["editing_course"] = course_id
                        if col2.button("删除", key=f"delete_{course_id}"):
                            delete_course(course_id)
                            st.success(f"已成功删除课程'{class_name}'")
                            st.experimental_rerun()

                        # Inline edit form for this course.
                        if "editing_course" in st.session_state and st.session_state["editing_course"] == course_id:
                            st.markdown("#### 编辑课程")
                            with st.form(key=f"edit_course_form_{course_id}"):
                                new_class_name = st.text_input("课程名", value=class_name)
                                new_subject = st.text_input("科目", value=subject)
                                new_grade = st.text_input("年级", value=grade)
                                new_course_desc = st.text_area("科目简介", value=course_desc)
                                new_teacher_desc = st.text_area("老师简介", value=teacher_desc)
                                new_max_students = st.number_input("最多可报名学生", value=int(max_students),
                                                                   min_value=1)
                                update_btn = st.form_submit_button("更新课程")
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
                                st.success("课程更新成功！")
                                del st.session_state["editing_course"]
                                st.experimental_rerun()
                            if st.button("取消编辑", key=f"cancel_edit_{course_id}"):
                                del st.session_state["editing_course"]
                                st.experimental_rerun()
                            st.markdown("---")
            else:
                st.info("没有搜索到课程")

        # -----------------------------------
        # (2) Create Course Section
        # -----------------------------------
        elif teacher_action == "创建课程":
            st.subheader("创建课程")
            with st.form("create_course_form"):
                course_name = st.text_input("课程名")
                course_subject = st.text_input("科目")
                course_grade = st.text_input("年级")
                course_description = st.text_area("科目简介")
                # Teacher Description is taken from teacher profile.
                st.markdown("老师简介将被自动加入")
                max_students = st.number_input("最多可报名人数", value=2, min_value=1)
                submit_course = st.form_submit_button("新建课程")
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
                st.success("课程创建成功！")
                st.experimental_rerun()

        # -----------------------------------
        # (3) Edit Profile Section
        # -----------------------------------
        elif teacher_action == "编辑个人信息":
            st.subheader("编辑个人信息")
            with st.form("edit_profile_form"):
                new_teacher_description = st.text_area("老师简介", value=st.session_state["teacher_description"])
                update_profile = st.form_submit_button("更新间接")
            if update_profile:
                update_teacher_description(st.session_state["teacher_name"], new_teacher_description)
                st.session_state["teacher_description"] = new_teacher_description
                st.success("以成功更新老师简介")
                st.experimental_rerun()
else:
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
