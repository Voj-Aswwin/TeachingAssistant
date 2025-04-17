import streamlit as st
import pyperclip
from modules.db_utils import add_to_db
from modules.pdf_generator import generate_pdf_of_rough_notes
from modules.summarization import get_gemini_response

def RoughBookPage():
    st.title("📝 Rough Book Page")
    st.markdown("Use this wide text box as your digital rough book. Jot down ideas, lists, or anything on your mind.")

    # Style the text area
    st.markdown("""
        <style>
        .stTextArea textarea {
            height: 400px;
            font-size: 16px;
            font-family: monospace;
            background-color: #fdf6e3;
        }
        </style>
        """, unsafe_allow_html=True)

    # Input box
    st.session_state['rough_notes'] = st.text_area(
        " ", 
        value=st.session_state['rough_notes'], 
        placeholder="Start typing your thoughts here...", 
        height=400
    )

    # Buttons: side by side
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("💾 Add Note to DB"):
            with st.spinner("💾 Saving note..."):
                pdf_path = generate_pdf_of_rough_notes(st.session_state['rough_notes'])
                add_to_db(pdf_path)
                st.success("Notes saved to DB")

    with col2:
        if st.button("🪄 Format Neatly"):
            with st.spinner("🧠 Formatting using AI..."):
                prompt = f"""
                “Rewrite the following notes into clear, well-structured plain text. 
                Avoid using Markdown or formatting symbols like *, #, or dashes. 
                Just use paragraphs, numbered steps, or plain line breaks for structure.”

                Notes:
                {st.session_state['rough_notes']}
                """
                formatted = get_gemini_response(prompt)
                st.session_state['rough_notes'] = formatted
                st.rerun()  # Force update to show formatted content in-place
    
    with col3:
        if st.button("📋 Copy to Clipboard"):
            pyperclip.copy(st.session_state['rough_notes'])
            st.success("Copied to clipboard!")