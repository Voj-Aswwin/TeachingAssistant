import streamlit as st
from modules.quiz_generator import generate_quiz, display_quiz

def QuizPage():
    # Generate Quiz

    if st.button("Generate Quiz", key="generate_quiz_button"):
        with st.spinner('Generating summary from Gemini...'):
            st.session_state['quiz_questions'] = generate_quiz(st.session_state.get('summary', ""))
    
    if st.session_state.get('quiz_questions'):
        display_quiz()