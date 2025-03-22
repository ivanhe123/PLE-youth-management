import streamlit as st
from streamlit_javascript import st_javascript


def go_to_url(url) -> None:

    st.html ( f"""
    <script>
        window.open("{url}", "_blank");
    </script>
    """)

def get_pages(language: str):
    """Return the list of pages based on the selected language."""

    url = st_javascript("await fetch('').then(r => window.parent.location.href)")

    if isinstance(url, str):
        url = url.split("/")

        if language == "中文 (Chinese)":
            if url[5] == "":
                st.switch_page("enrollment_forum_mand")
            else:
                st.switch_page(url[5] + "_mand")
        else:
            if url[5] == "":
                st.switch_page("enrollment_forum")
            else:
                st.switch_page(url[5].replace("_mand",""))

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
            st.Page("enrollment_forum_mand.py"),
            st.Page("admin_panel_mand.py"),

            st.Page("teacher_panel_mand.py")
        ]

nav = st.navigation(pages=pages, position="hidden")
get_pages(selected_language)

nav.run()
