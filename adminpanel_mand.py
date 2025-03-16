# admin_panel.py

import streamlit as st
import json
from teacher_db import (
    init_teacher_db,
    get_all_teachers,
    update_teacher_credentials,  # Updates both passcode and teacher description.
    update_teacher_description,
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
st.set_page_config(page_title="管理员面板", layout="wide")
st.title("管理员面板")

# Initialize both databases.
init_teacher_db()
init_courses_db()

# ---------------------------
# ADMIN LOGIN SECTION
# ---------------------------
if "admin_logged_in" not in st.session_state:
    st.session_state["admin_logged_in"] = False

if not st.session_state["admin_logged_in"]:
    st.subheader("管理员登录")
    admin_passcode = st.text_input("管理员密码：", type="password")
    if st.button("登入"):
        if admin_passcode == "1234":
            st.session_state["admin_logged_in"] = True
            st.success("管理登入成功！")
        else:
            st.error("管理员登入失败！")

# ---------------------------
# MAIN ADMIN FUNCTIONALITIES
# ---------------------------
if st.session_state.get("admin_logged_in"):

    # Sidebar: Choose between impersonation and normal course management.
    admin_mode = st.sidebar.radio("管理员选项", ["化身老师", "管理课程"])

    # ============================
    # IMPERSONATE TEACHER SECTION
    # ============================
    if admin_mode == "化身老师":
        st.header("化身老师")
        # If we are already impersonating a teacher, show the teacher panel.
        if "impersonated_teacher" in st.session_state:
            teacher_name = st.session_state["impersonated_teacher"]
            teacher_desc = st.session_state.get("impersonated_teacher_description", "")
            st.info(f"现在化身的老师: **{teacher_name}**")
            if st.button("变回管理员"):
                del st.session_state["impersonated_teacher"]
                if "impersonated_teacher_description" in st.session_state:
                    del st.session_state["impersonated_teacher_description"]
                st.experimental_rerun()

            # Teacher Panel Functionalities (impersonated)
            teacher_action = st.radio("老师选项", ("我的课程", "新建课程", "编辑个人信息"))

            # (1) View My Courses
            if teacher_action == "我的课程":
                st.subheader("我的课程")
                search_query = st.text_input("搜索我的课程", placeholder="输入课程名...", key="teacher_search")
                # Get courses only created by the impersonated teacher.
                def get_teacher_courses():
                    return [c for c in get_all_courses() if c[2] == teacher_name]
                my_courses = get_teacher_courses()
                if search_query:
                    filtered_courses = []
                    q = search_query.lower()
                    for course in my_courses:
                        # Course record:
                        # (id, class_name, teacher, subject, grade, course_desc, teacher_desc, max_students, enrolled_students)
                        if (q in course[1].lower() or q in course[3].lower() or
                            q in course[4].lower() or q in course[5].lower() or
                            q in course[6].lower()):
                            filtered_courses.append(course)
                    display_courses = filtered_courses
                else:
                    display_courses = my_courses

                if display_courses:
                    for course in display_courses:
                        (course_id, class_name, teacher, subject, grade, course_desc, teacher_desc, max_students, enrolled_students) = course
                        try:
                            enrolled_list = json.loads(enrolled_students)
                        except Exception:
                            enrolled_list = []
                        num_enrolled = len(enrolled_list)
                        with st.container():
                            st.markdown(f"### {class_name}")
                            st.markdown(f"**科目:** {subject} | **年级:** {grade} | **最多可报名人数:** {max_students} | **已报名人数:** {num_enrolled}")
                            st.markdown(f"**课程简介:** {course_desc}")
                            st.markdown(f"**老师简介:** {teacher_desc}")
                            with st.expander("以报名的学生"):
                                if enrolled_list:
                                    for s in enrolled_list:
                                        st.write(s)
                                else:
                                    st.write("还没有学生报名")
                            col1, col2 = st.columns(2)
                            if col1.button("编辑", key=f"t_edit_{course_id}"):
                                st.session_state["t_editing_course"] = course_id
                            if col2.button("删除", key=f"t_delete_{course_id}"):
                                delete_course(course_id)
                                st.success(f"课程'{class_name}'已被删除.")
                                st.experimental_rerun()

                            if "t_editing_course" in st.session_state and st.session_state["t_editing_course"] == course_id:
                                st.markdown("#### 编辑课程")
                                with st.form(key=f"t_edit_form_{course_id}"):
                                    new_class_name = st.text_input("课程名字", value=class_name)
                                    new_subject = st.text_input("科目", value=subject)
                                    new_grade = st.text_input("年级", value=grade)
                                    new_course_desc = st.text_area("课程简介", value=course_desc)
                                    new_teacher_desc = st.text_area("老师简介", value=teacher_desc)
                                    new_max_students = st.number_input("最多可报名人数", value=int(max_students), min_value=1)
                                    update_btn = st.form_submit_button("更新课程")
                                if update_btn:
                                    update_course(
                                        course_id,
                                        new_class_name,
                                        teacher_name,  # Impersonated teacher remains the owner.
                                        new_subject,
                                        new_grade,
                                        new_course_desc,
                                        new_teacher_desc,
                                        new_max_students,
                                        json.dumps(enrolled_list)
                                    )
                                    st.success("课程成功更新!")
                                    del st.session_state["t_editing_course"]
                                    st.experimental_rerun()
                                if st.button("取消编辑", key=f"t_cancel_edit_{course_id}"):
                                    del st.session_state["t_editing_course"]
                                    st.experimental_rerun()
                                st.markdown("---")
                else:
                    st.info("这个老师还没有课程")

            # (2) Create Course
            elif teacher_action == "新建课程":
                st.subheader("新建课程")
                with st.form("teacher_create_course_form"):
                    course_name = st.text_input("课程名")
                    subject = st.text_input("科目")
                    grade = st.text_input("年级")
                    course_desc = st.text_area("课程简介")
                    st.markdown("老师简介将被自动加入")
                    max_students = st.number_input("最多可报名人数", value=2, min_value=1)
                    submit_course = st.form_submit_button("新建课程")
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
                    st.success("新建课程成功！")
                    st.experimental_rerun()

            # (3) Edit Profile
            elif teacher_action == "编辑个人信息":
                st.subheader("编辑个人信息")
                with st.form("teacher_edit_profile_form"):
                    new_teacher_desc = st.text_area("老师简介", value=teacher_desc)
                    update_profile = st.form_submit_button("更新老师信息")
                if update_profile:
                    update_teacher_description(teacher_name, new_teacher_desc)
                    st.success("老师信息更新成功！")
                    st.session_state["impersonated_teacher_description"] = new_teacher_desc
                    st.experimental_rerun()
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

        else:
            # If not impersonating, show the teacher search interface.
            st.subheader("搜索要化身的老师")
            search_teacher_input = st.text_input("搜索老师", placeholder="输入老师名...")
            teacher_profiles = get_all_teachers()
            if search_teacher_input:
                filtered_teachers = [t for t in teacher_profiles if search_teacher_input.lower() in t[1].lower()]
            else:
                filtered_teachers = teacher_profiles

            if filtered_teachers:
                for teacher in filtered_teachers:
                    tid, t_name, t_pass, t_desc = teacher
                    with st.container():
                        st.markdown(f"#### {t_name}")
                        st.markdown(f"**简介:** {t_desc if t_desc else 'No description available.'}")
                        if st.button("化身", key=f"login_as_{tid}"):
                            st.session_state["impersonated_teacher"] = t_name
                            st.session_state["impersonated_teacher_description"] = t_desc if t_desc else ""
                            st.experimental_rerun()
                        st.markdown("---")
            else:
                st.info("没有找到老师")

    # ============================
    # MANAGE COURSES SECTION (Admin mode)
    # ============================
    elif admin_mode == "管理课程":
        st.header("管理课程")
        search_course = st.text_input("搜索课程", placeholder="输入课程名...", key="admin_search_course")
        all_courses = get_all_courses()
        # Each course record: (id, class_name, teacher, subject, grade, course_desc, teacher_desc, max_students, enrolled_students)
        if search_course:
            filtered_courses = []
            q = search_course.lower()
            for c in all_courses:
                if (q in c[1].lower() or q in c[2].lower() or q in c[3].lower() or
                    q in c[4].lower() or q in c[5].lower() or q in c[6].lower()):
                    filtered_courses.append(c)
        else:
            filtered_courses = all_courses

        if filtered_courses:
            for course in filtered_courses:
                (course_id, class_name, teacher, subject, grade, course_desc, teacher_desc, max_students, enrolled_students) = course
                try:
                    enrolled_list = json.loads(enrolled_students)
                except Exception:
                    enrolled_list = []
                num_enrolled = len(enrolled_list)
                with st.container():
                    st.markdown(f"### {class_name}")
                    st.markdown(f"**老师:** {teacher} | **科目:** {subject} | **年级:** {grade}")
                    st.markdown(f"**课程简介:** {course_desc}")
                    st.markdown(f"**老师简介:** {teacher_desc}")
                    st.markdown(f"**最多可报名人数:** {max_students} | **已报名人数:** {num_enrolled}")
                    with st.expander("已报名的学生"):
                        if enrolled_list:
                            for s in enrolled_list:
                                st.write(s)
                        else:
                            st.write("还没有学生报名")
                    col1, col2, col3, col4 = st.columns(4)
                    if col1.button("编辑", key=f"admin_edit_{course_id}"):
                        st.session_state["admin_editing_course"] = course_id
                    if col2.button("删除", key=f"admin_delete_{course_id}"):
                        delete_course(course_id)
                        st.success(f"课程'{class_name}'已被成功删除！")
                        st.experimental_rerun()
                    if col3.button("编辑报名名单", key=f"admin_edit_enrollment_{course_id}"):
                        st.session_state["admin_editing_enrollment"] = course_id
                    if col4.button("取消报名名单编辑", key=f"admin_cancel_enrollment_{course_id}"):
                        if "admin_editing_enrollment" in st.session_state and st.session_state["admin_editing_enrollment"] == course_id:
                            del st.session_state["admin_editing_enrollment"]
                            st.experimental_rerun()

                    if "admin_editing_enrollment" in st.session_state and st.session_state["admin_editing_enrollment"] == course_id:
                        st.markdown("#### 编辑报名名单")
                        for idx, student in enumerate(enrolled_list):
                            colA, colB = st.columns([3,1])
                            colA.write(student)
                            if colB.button("移除", key=f"admin_remove_{course_id}_{idx}"):
                                removed = enrolled_list.pop(idx)
                                new_enrolled_json = json.dumps(enrolled_list)
                                update_course(course_id, class_name, teacher, subject, grade, course_desc, teacher_desc, max_students, new_enrolled_json)
                                st.success(f"学生'{removed}'已被移除")
                                st.experimental_rerun()
                        with st.form(key=f"admin_add_student_form_{course_id}"):
                            new_student = st.text_input("新学生名")
                            add_student_btn = st.form_submit_button("给学生报名")
                        if add_student_btn:
                            if new_student.strip() != "":
                                if len(enrolled_list) < max_students:
                                    enrolled_list.append(new_student.strip())
                                    new_enrolled_json = json.dumps(enrolled_list)
                                    update_course(course_id, class_name, teacher, subject, grade, course_desc, teacher_desc, max_students, new_enrolled_json)
                                    st.success(f"学生'{new_student}'报名成功")
                                    st.experimental_rerun()
                                else:
                                    st.error("课程已满")
                            else:
                                st.error("请输入正确学生名")
                        if st.button("完成编辑", key=f"admin_finish_edit_{course_id}"):
                            if "admin_editing_enrollment" in st.session_state:
                                del st.session_state["admin_editing_enrollment"]
                                st.experimental_rerun()

                    if "admin_editing_course" in st.session_state and st.session_state["admin_editing_course"] == course_id:
                        st.markdown("#### 编辑课程")
                        with st.form(key=f"admin_edit_course_form_{course_id}"):
                            new_class_name = st.text_input("课程名", value=class_name)
                            new_teacher = st.text_input("老师", value=teacher)
                            new_subject = st.text_input("科目", value=subject)
                            new_grade = st.text_input("年级", value=grade)
                            new_course_desc = st.text_area("科目简介", value=course_desc)
                            new_teacher_desc = st.text_area("老师简介", value=teacher_desc)
                            new_max_students = st.number_input("最多可报名人数", value=int(max_students), min_value=1)
                            update_btn = st.form_submit_button("更新课程")
                        if update_btn:
                            update_course(course_id, new_class_name, new_teacher, new_subject, new_grade, new_course_desc, new_teacher_desc, new_max_students, json.dumps(enrolled_list))
                            st.success("课程更新成功")
                            del st.session_state["admin_editing_course"]
                            st.experimental_rerun()
                        if st.button("取消编辑", key=f"admin_cancel_edit_{course_id}"):

                            del st.session_state["admin_editing_course"]
                            st.experimental_rerun()
                        st.markdown("---")
        else:
            st.info("没有搜索到课程")

