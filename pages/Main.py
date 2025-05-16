import streamlit as st
from modules.summarization import get_gemini_response
from modules.pdf_generator import generate_pdf_of_youtube_summaries
from modules.db_utils import add_to_db
from modules.youtube_utils import fetch_transcript
from modules.data_extraction import extract_numerical_data
from modules.ask_questions import ask_question, write_conversation_history
from modules.timeline_generator import extract_timeline
import requests
from bs4 import BeautifulSoup

def is_youtube_url(url):
    return "youtube.com/watch" in url or "youtu.be" in url


def MainPage():
    st.title("YouTube Video Analysis & Quiz Generator")

    col1, col2 = st.columns([4, 1])
    with col1:
        input_url = st.text_input("Enter a URL (YouTube or Website)", placeholder="Enter the URL here...")
    with col2:
        st.markdown("<div style='height: 1.7em;'></div>", unsafe_allow_html=True)
        if st.button("Add", key="add_url_button"):
            if input_url.strip() == "":
                st.error("Please enter a valid URL.")
            elif input_url in st.session_state['youtube_urls']:
                st.warning("This URL is already added.")
            else:
                st.session_state['youtube_urls'].append(input_url)

    # Display list of added URLs with remove buttons
    if st.session_state['youtube_urls']:
        st.subheader("📚 Added URLs")
        for idx, url in enumerate(st.session_state['youtube_urls']):
            col1, col2 = st.columns([8, 1])
            with col1:
                st.markdown(f"- {url}")
            with col2:
                if st.button("❌", key=f"remove_{idx}"):
                    st.session_state['youtube_urls'].pop(idx)
                    st.rerun()

    st.subheader("Fetch Transcripts and Generate Summary")
    if st.button("Fetch Summary", key="fetch_summary_button"):
        if not st.session_state['youtube_urls']:
            st.error("Please add at least one YouTube URL.")
        else:
            st.session_state['transcripts'] = []
            for url in st.session_state['youtube_urls']:
                if is_youtube_url(url):
                    transcript_content, error = fetch_transcript(url)
                    if error:
                        st.error(f"Error fetching transcript for {url}: {error}")
                    else:
                        st.session_state['transcripts'].append(transcript_content)
                else:
                    try:
                        response = requests.get(url, timeout=10)
                        response.raise_for_status()
                        soup = BeautifulSoup(response.text, "html.parser")
                        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                            tag.decompose()
                        text = soup.get_text(separator="\n")
                        clean_lines = [line.strip() for line in text.splitlines() if line.strip()]
                        page_content = "\n".join(clean_lines)
                        st.session_state['transcripts'].append(page_content[:10000])
                    except Exception as e:
                        st.error(f"Failed to fetch website content from {url}: {e}")
                combined_transcripts = "\n\n".join(st.session_state['transcripts'])

        with st.spinner('Generating summary from Gemini...'):
            summary_prompt = 'Summarize the text briefly but keep all key points using headers and bullet points.'
            gemini_response = get_gemini_response(combined_transcripts + summary_prompt, model_name="gemini-2.0-flash")
        
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
    if st.session_state['conversation_history']:
            write_conversation_history()
    question = st.text_input("Your Question", placeholder="Ask something about the transcript...")
    if st.button("Get Answer"):
        answer = ask_question(question, st.session_state['combined_transcripts']) 
        
        

    # Add Summary to DB

    if st.button("Save Summary to DB"):
        
        pdf_file = generate_pdf_of_youtube_summaries()

        # ✅ Run filldb.py to process the PDF into ChromaDB
        add_to_db(pdf_file)