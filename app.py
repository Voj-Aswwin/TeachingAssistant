import streamlit as st
from modules.ui_components import setup_sidebar
from pages.Main import MainPage
from pages.QuizPage import QuizPage
from pages.TalkToDBPage import TalkToDBPage
from pages.RoughBookPage import RoughBookPage
from pages.TeachAndLearnPage import TeachAndLearnPage


st.set_page_config(layout="wide", page_title="YouTube Video Analysis")

# Initialize session state variables

if 'quiz_questions' not in st.session_state:
    st.session_state['quiz_questions'] = None
if 'summary' not in st.session_state:
    st.session_state['summary'] = None    
if 'youtube_urls' not in st.session_state:
    st.session_state['youtube_urls'] = []    
if 'selected_function' not in st.session_state:
    st.session_state['selected_function'] = "main"
if 'numerical_data' not in st.session_state:
    st.session_state['numerical_data'] = None
if 'extracted_timeline' not in st.session_state:
    st.session_state['extracted_timeline'] = None
if 'conversation_history' not in st.session_state:
    st.session_state['conversation_history'] = []        
if 'db_conversation' not in st.session_state:
    st.session_state['db_conversation'] = []
if 'rough_notes' not in st.session_state:
    st.session_state['rough_notes'] = None   
if "fp_chat_history" not in st.session_state:
        st.session_state['fp_chat_history'] = []

setup_sidebar()

if st.session_state.page == "Main":
    
    MainPage()
    
elif st.session_state.page == "Quiz":

    QuizPage()

elif st.session_state.page == "Talk to DB":

    TalkToDBPage()

elif st.session_state.page == "Rough Book":

    RoughBookPage()

elif st.session_state.page == "Teach And Learn":

    TeachAndLearnPage()     