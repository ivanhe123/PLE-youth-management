# enrollment_forum.py

import streamlit as st
import json
from courses_db import init_courses_db, get_all_courses, update_course

st.set_page_config(page_title="报名", layout="wide")
st.title("报名")

# Initialize (or ensure) the courses database is ready.
init_courses_db()
st.experimental_rerun=st.rerun
# ---------------------------
# Search and Filter Courses
# ---------------------------
search_query = st.text_input("搜索课程", placeholder="输入任意关键词（老师名，课程名，简介，年级，科目）")

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
    st.markdown(f"**老师名:** {teacher} | **科目:** {subject} | **年级:** {grade}")
    st.markdown(f"**课程简介:** {course_desc}")
    st.markdown(f"**老师简介:** {teacher_desc}")
    st.markdown(f"**做多可报名人数:** {max_students} | **已报名人数:** {num_enrolled}")

    # ---------------------------------------
    # Enrollment Button with Threshold Check
    # ---------------------------------------
    if num_enrolled >= max_students:
        st.button("报名", key=f"enroll_{course_id}", disabled=True)
        st.info("课程已满")
    else:
        if st.button("报名", key=f"enroll_{course_id}"):
            # Store the course ID in session state to trigger enrollment form.
            st.session_state["enroll_course_id"] = course_id
            st.experimental_rerun()

    # ---------------------------------------
    # Enrollment Form (only for the selected course)
    # ---------------------------------------
    if "enroll_course_id" in st.session_state and st.session_state["enroll_course_id"] == course_id:
        st.markdown("### 报名")
        with st.form(key=f"enroll_form_{course_id}"):
            student_name = st.text_input("输入你的名字")
            enroll_submit = st.form_submit_button("提交")
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
                st.success(f"{student_name}以报名！")
                del st.session_state["enroll_course_id"]
                st.experimental_rerun()
            else:
                st.error("请输入你的名字")
        if st.button("取消报名", key=f"cancel_enroll_{course_id}"):
            del st.session_state["enroll_course_id"]
            st.experimental_rerun()

    # ---------------------------------------
    # Expandable Section for Enrolled Students
    # ---------------------------------------
    with st.expander("查看以报名的学生"):
        if enrolled_list:
            for student in enrolled_list:
                st.write(student)
        else:
            st.write("还没有学生报名")

    st.markdown("---")
