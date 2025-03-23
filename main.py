import streamlit as st

# Store selected language in session state
if "selected_language" not in st.session_state:
    st.session_state.selected_language = "English (英语)"

lang_options = ["English (英语)", "中文 (Chinese)"]
selected_language = st.sidebar.selectbox("Select Language/选择语言", lang_options)
st.session_state.selected_language = selected_language
