import streamlit as st

# Retrieve query parameters (if any)
params = st.experimental_get_query_params()
current_page = params.get("page", [None])[0]  # e.g., "admin_panel"

lang_options = ["English (英语)", "中文 (Chinese)"]
selected_language = st.sidebar.selectbox("Select Language/选择语言", lang_options)
# Optionally update query params with a language flag
st.experimental_set_query_params(lang=selected_language, page=current_page)

def get_pages(language: str):
    # Ideally, use a mapping to preserve a common page identifier
    pages_map = {
        "enrollment_forum": {
            "English (英语)": "enrollment_forum.py",
            "中文 (Chinese)": "enrollment_forum_mand.py"
        },
        "admin_panel": {
            "English (英语)": "admin_panel.py",
            "中文 (Chinese)": "admin_panel_mand.py"
        },
        "teacher_panel": {
            "English (英语)": "teacher_panel.py",
            "中文 (Chinese)": "teacher_panel_mand.py"
        },
    }
    # Build pages list from the mapping.
    pages = []
    for identifier, files in pages_map.items():
        pages.append(st.Page(files[selected_language], key=identifier))
    return pages

pages = get_pages(selected_language)
nav = st.navigation(pages=pages, position="hidden")
nav.run()
