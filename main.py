import streamlit as st

pages= [ st.Page("enrollment_forum.py"), st.Page("admin_panel.py"), st.Page("teacher_panel.py"), ]
nav = st.navigation(pages=pages, position="hidden")
nav.run()