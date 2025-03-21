import streamlit as st

def get_pages(language: str):
    """Return the list of pages based on the selected language."""

    if language == "English (英语)":
        return [
            st.Page("admin_panel.py"),
            st.Page("enrollment_forum.py"),
            st.Page("teacher_panel.py"),
        ]
    elif language == "中文 (Chinese)":
        return [
            st.Page("admin_panel_mand.py"),
            st.Page("enrollment_forum_mand.py"),
            st.Page("teacher_panel_mand.py"),
        ]


# Add a language dropdown to the sidebar.
# Using an on_change callback with st.experimental_rerun ensures the app refreshes when selection changes.
lang_options = ["English (英语) ", "中文 (Chinese)"]
selected_language = st.sidebar.selectbox(
    "Select Language/选择一个语言",
    lang_options, 
    key="language",
    on_change=lambda: st.rerun()
)


# Get the appropriate pages based on the selected language.
pages = get_pages(selected_language)
nav = st.navigation(pages=pages, position="hidden")
nav.run()
