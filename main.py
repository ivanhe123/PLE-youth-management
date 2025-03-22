import streamlit as st
from streamlit_javascript import st_javascript



# Get the appropriate pages based on the selected language.
pages = [
            st.Page("enrollment_forum.py"),
            st.Page("admin_panel.py"),

            st.Page("teacher_panel.py"),
        ]

nav = st.navigation(pages=pages, position="hidden")


nav.run()
