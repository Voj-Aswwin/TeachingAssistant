import streamlit as st
from modules.db_utils import add_to_db
from modules.pdf_generator import generate_pdf_of_rough_notes

def RoughBookPage():
    # Page to Note Down 

    # Title / Header
    st.title("📝 Rough Book Page")

    # Optional: Description
    st.markdown("Use this wide text box as your digital rough book. Jot down ideas, lists, or anything on your mind.")

    # Style tweak for larger text area
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

    # The actual wide text box
    st.session_state['rough_notes'] = st.text_area(" ", value=st.session_state['rough_notes'], placeholder="Start typing your thoughts here...", height=400)

    # Optional: Save or export logic
    if st.button("💾 Add Note to DB"):
        with st.spinner("💾 Saving note"):
            pdf_path = generate_pdf_of_rough_notes(st.session_state['rough_notes'])
            add_to_db(pdf_path)
            st.success("Notes saved to DB")
        