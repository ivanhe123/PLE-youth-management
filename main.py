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
url = st_javascript("window.parent.location.href")


if isinstance(url, str):
    url=url.split("/")
else:
    st.rerun()
#st.write(url[2]+"/"+url[5])
if lang_options == "中文 (Chinese)":
    pages = url[2]+"/"+url[5], [
        st.Page("enrollment_forum_mand.py"),
        st.Page("admin_panel_mand.py"),

        st.Page("teacher_panel_mand.py"),
    ]
else:
    pages = url[2]+"/"+url[5], [
        st.Page("enrollment_forum.py"),
        st.Page("admin_panel.py"),

        st.Page("teacher_panel.py"),
    ]

nav = st.navigation(pages=pages[1], position="hidden")
go_to_url(pages[0])

nav.run()
