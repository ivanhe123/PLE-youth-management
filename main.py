from itertools import compress
from time import sleep

import streamlit as st


pages = [
    st.Page("adminpanel2.py"),
    st.Page("enrollment_forum.py"),
    st.Page("teacher_panel.py"),
]

nav = st.navigation(pages=pages, position="hidden")

### App layout

"""for page in pages:
    st.page_link(page)"""

nav.run()