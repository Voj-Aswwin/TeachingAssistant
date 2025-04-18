import streamlit as st
from modules.summarization import get_gemini_response
from modules.pdf_generator import generate_pdf_of_youtube_summaries
from modules.db_utils import add_to_db
from modules.youtube_utils import fetch_transcript
from modules.data_extraction import extract_numerical_data
from modules.ask_questions import ask_question, write_conversation_history
from modules.timeline_generator import extract_timeline

def MainPage():
    st.title("YouTube Video Analysis & Quiz Generator")

    youtube_url = st.text_input("Add a YouTube URL", placeholder="Enter the URL here...")
    if st.button("Add URL", key="add_url_button"):
        if youtube_url.strip() == "":
            st.error("Please enter a valid YouTube URL.")
        elif youtube_url in st.session_state['youtube_urls']:
            st.warning("This URL is already added.")
        else:
            st.session_state['youtube_urls'].append(youtube_url)
            st.success("URL added successfully.")

    st.subheader("Fetch Transcripts and Generate Summary")
    if st.button("Fetch Summary", key="fetch_summary_button"):
        if not st.session_state['youtube_urls']:
            st.error("Please add at least one YouTube URL.")
        else:
            st.session_state['transcripts'] = []
            for url in st.session_state['youtube_urls']:
                transcript_content, error = fetch_transcript(url)
                if error:
                    st.error(f"Error fetching transcript for {url}: {error}")
                else:
                    st.session_state['transcripts'].append(transcript_content)
            
            combined_transcripts = "\n\n".join(st.session_state['transcripts'])
            summary_prompt = 'Summarize the text briefly but keep all key points using headers and bullet points.'

            with st.spinner('Generating summary from Gemini...'):
                gemini_response = get_gemini_response(combined_transcripts + summary_prompt)
            
            st.session_state['summary'] = gemini_response
            st.session_state['combined_transcripts'] = combined_transcripts
    
    if st.session_state['summary']:
        st.write(st.session_state['summary'])

    # Extract Numerical Data    

    if st.button("Extract Numbers", key="extract_numericals"):
        with st.spinner("Extracting Numerical Data"):
            st.session_state['numerical_data'] = extract_numerical_data(st.session_state["summary"])
    if st.session_state['numerical_data']: st.markdown(st.session_state['numerical_data'])
    
    # Generate Timeline

    if st.button("Generate Timeline", key="generate_timeline_button"):
        with st.spinner("Generating timeline..."):
            st.session_state['extracted_timeline'] = extract_timeline(st.session_state["summary"])
    if st.session_state['extracted_timeline']: st.markdown(st.session_state['extracted_timeline'])
    
    # Ask Questions about Summary
    
    st.subheader("Ask Questions")
    question = st.text_input("Your Question", placeholder="Ask something about the transcript...")
    if st.button("Get Answer"):
        answer = ask_question(question, st.session_state['combined_transcripts'])   
    if st.session_state['conversation_history']:
        write_conversation_history()

    # Add Summary to DB

    if st.button("Save Summary to DB"):
        
        pdf_file = generate_pdf_of_youtube_summaries()

        # ✅ Run filldb.py to process the PDF into ChromaDB
        add_to_db(pdf_file)