import streamlit as st

def setup_sidebar():
    """Creates sidebar navigation in Streamlit."""
    st.sidebar.title("Navigation")

    if "page" not in st.session_state:
        st.session_state.page = "Main"  # Default page

    if st.sidebar.button("Main Page"):
        st.session_state.page = "Main"
    if st.sidebar.button("Quiz Page"):
        st.session_state.page = "Quiz"
    if st.sidebar.button("Talk to DB"):
        st.session_state.page = "Talk to DB"

def show_summary(summary):
    """Displays summary in Streamlit."""
    if summary:
        st.write(summary)
    else:
        st.warning("No summary generated yet.")
