import streamlit as st

def setup_sidebar():
    """Creates sidebar navigation in Streamlit."""
    st.sidebar.title("Navigation")

    if "page" not in st.session_state:
        st.session_state.page = "YoutubeSummarizer"  # Default page

    if st.sidebar.button("Youtube Summarizer Page"):
        st.session_state.page = "YoutubeSummarizer"
    if st.sidebar.button("Quiz Page"):
        st.session_state.page = "Quiz"
    if st.sidebar.button("Talk to DB"):
        st.session_state.page = "Talk to DB"
    if st.sidebar.button("Rough Book"):
        st.session_state.page = "Rough Book"    
    if st.sidebar.button("Teach And Learn"):
        st.session_state.page = "Teach And Learn"
    if st.sidebar.button("Live Transcribe"):
        st.session_state.page = "Live Transcribe"

def show_summary(summary):
    """Displays summary in Streamlit."""
    if summary:
        st.write(summary)
    else:
        st.warning("No summary generated yet.")
