import streamlit as st 
from .summarization import get_gemini_response

def ask_question(query, transcript):
    """Retrieves relevant information from transcript based on user query"""
    if query.strip():
            with st.spinner("Generating response..."):
                full_prompt = transcript + "\nQ: " + query
                response = get_gemini_response(full_prompt)
                st.session_state['conversation_history'].append((query, response))
                st.rerun() 
    return response        

def write_conversation_history():
     for i, (q, a) in enumerate(st.session_state['conversation_history']):
            st.write(f"**Q{i+1}:** {q}")
            st.write(f"**A{i+1}:** {a}")

# Example Usage
if __name__ == "__main__":
    question = "What are the key takeaways from the video?"
    print(ask_question(question))
