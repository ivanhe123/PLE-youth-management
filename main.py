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
url = st_javascript("window.parent.location.href")


if isinstance(url, str):
    url=url.split("/")
st.write(url[2])
if selected_language == "中文 (Chinese)":
    pages =  [
        st.Page("enrollment_forum_mand.py"),
        st.Page("admin_panel_mand.py"),

        st.Page("teacher_panel_mand.py"),
    ]
else:
    pages= [
        st.Page("enrollment_forum.py"),
        st.Page("admin_panel.py"),

        st.Page("teacher_panel.py"),
    ]
go_to_url(url[2]+"/"+url[5])

nav = st.navigation(pages=pages, position="hidden")


nav.run()
