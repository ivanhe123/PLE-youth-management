import streamlit as st
from streamlit_javascript import st_javascript


def go_to_url(url) -> None:

    st.html ( f"""
    <script>
        window.open("{url}", "_blank");
    </script>
    """)


# Add a language dropdown to the sidebar.
# Using an on_change callback with st.experimental_rerun ensures the app refreshes when selection changes.
lang_options = ["English (英语) ", "中文 (Chinese)"]
selected_language = st.sidebar.selectbox(
    "Select Language/选择一个语言",
    lang_options,
)


# Get the appropriate pages based on the selected language.
pages = [
            st.Page("enrollment_forum.py"),
            st.Page("admin_panel.py"),

            st.Page("teacher_panel.py"),
        ]

nav = st.navigation(pages=pages, position="hidden")


nav.run()
