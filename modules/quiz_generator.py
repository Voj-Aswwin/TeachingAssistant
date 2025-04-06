import json
import streamlit as st
from .summarization import get_gemini_response

def generate_quiz(transcripts):
    """Generates MCQs based on video transcripts."""
    quiz_prompt = (
        "Generate 5 MCQs from the transcript. "
        "Each question must have four options in a list and provide the correct answer."
        "Return the response in valid JSON format as a list of dictionaries: "
        "[{'question': str, 'options': list, 'answer': str}]."
    )
    
    quiz_response = get_gemini_response(transcripts + quiz_prompt)

    try:
        quiz_response = quiz_response.strip().strip("```json").strip("```")
        quiz_response = json.loads(quiz_response)
        st.success("Quiz generated!")
        return quiz_response
    except json.JSONDecodeError:
        st.error("Failed to generate quiz.")

def display_quiz():
    user_answers = {}
    for idx, q in enumerate(st.session_state['quiz_questions']):
        user_answers[f'q{idx}'] = st.radio(q['question'], q['options'], key=f'quiz_q{idx}')

    if st.button("Submit Quiz", key="submit_quiz_button"):
        score = 0
        results = []
        for idx, q in enumerate(st.session_state['quiz_questions']):
            selected = user_answers[f'q{idx}']
            correct = q['answer']
            if selected == correct:
                score += 1
            results.append(f"**Q{idx+1}:** {q['question']}  \n**Your Answer:** {selected}  \n**Correct Answer:** {correct}\n")

        st.subheader(f"Your Score: {score}/{len(st.session_state['quiz_questions'])}")
        with st.expander("View Answers"):
            for result in results:
                st.markdown(result)
