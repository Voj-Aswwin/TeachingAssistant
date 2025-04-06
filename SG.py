import streamlit as st
import re
import google.generativeai as genai
import os
import json
from youtube_transcript_api import YouTubeTranscriptApi
from fpdf import FPDF
import subprocess
import chromadb

# Page Layout Configuration
st.set_page_config(layout="wide", page_title="YouTube Video Analysis")

# Function to extract YouTube video ID
def get_video_id(url):
    video_id = re.search(r'v=([a-zA-Z0-9_-]{11})', url)
    return video_id.group(1) if video_id else None

# 🔹 Connect to ChromaDB
CHROMA_PATH = r"chroma_db"
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name="youtube_summaries")

# Function to fetch YouTube transcript
def fetch_transcript(url):
    video_id = get_video_id(url)
    if not video_id:
        return None, "Invalid YouTube URL"
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([entry['text'] for entry in transcript])
        return transcript_text, None
    except Exception as e:
        return None, f"Error: {str(e)}"

# Function to generate AI response using Gemini
def get_gemini_response(prompt):
    try:
        genai.configure(api_key=os.environ["API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating content: {str(e)}"

def generate_pdf():

    # ✅ Ensure 'data' folder exists
    data_folder = "data"
    os.makedirs(data_folder, exist_ok=True)

    # ✅ Set PDF file path
    pdf_path = os.path.join(data_folder, "summary.pdf")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ✅ Use a Unicode-compatible font (built-in)
    pdf.set_font("Helvetica", size=12)
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)

    # Add Summary
    pdf.cell(200, 10, "Summary", ln=True, align='C')
    pdf.ln(10)
    summary = st.session_state.get('gemini_summary', "No summary generated yet.")
    pdf.multi_cell(190, 10, summary.encode("latin-1", "replace").decode("latin-1"))  # ✅ Handle encoding
    pdf.ln(10)

    # Add Questions and Answers
    pdf.cell(200, 10, "Questions & Answers", ln=True, align='C')
    pdf.ln(10)
    for i, (q, a) in enumerate(st.session_state.get('conversation_history', [])):
        # ✅ Reset indentation before each question
        pdf.set_x(10)
        pdf.multi_cell(0, 10, f"Q{i+1}: {q}".encode("latin-1", "replace").decode("latin-1"))
        
        # ✅ Reset indentation before each answer
        pdf.set_x(10)
        pdf.multi_cell(0, 10, f"A{i+1}: {a}".encode("latin-1", "replace").decode("latin-1"))
        
        pdf.ln(5)  # ✅ Add spacing for readability

    pdf.output(pdf_path)
    return pdf_path

# Initialize session state variables
if 'youtube_urls' not in st.session_state:
    st.session_state['youtube_urls'] = []
if 'transcripts' not in st.session_state:
    st.session_state['transcripts'] = []
if 'gemini_summary' not in st.session_state:
    st.session_state['gemini_summary'] = None
if 'timeline' not in st.session_state:
    st.session_state['timeline'] = None
if 'numerical_data' not in st.session_state:
    st.session_state['numerical_data'] = None
if 'conversation_history' not in st.session_state:
    st.session_state['conversation_history'] = []
if 'mcq_questions' not in st.session_state:
    st.session_state['mcq_questions'] = None
if 'selected_function' not in st.session_state:
    st.session_state['selected_function'] = "main"

# Sidebar Navigation
st.sidebar.title("Navigation")

if "page" not in st.session_state:
    st.session_state.page = "Main"  # Default page

if st.sidebar.button("Main Page"):
    st.session_state.page = "Main"
if st.sidebar.button("Quiz Page"):
    st.session_state.page = "Quiz"
if st.sidebar.button("Talk to DB"):
    st.session_state.page = "Talk to DB"
        

# Main Content
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

if st.session_state.page == "Main":
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
            
            st.session_state['gemini_summary'] = gemini_response
            st.session_state['combined_transcripts'] = combined_transcripts
    
    if st.session_state['gemini_summary']:
        st.write(st.session_state['gemini_summary'])

    # Extract Numerical Data
    # st.subheader("Extract Numerical Data")
    if st.button("Extract Data", key="extract_data_button"):
        with st.spinner("Extracting numerical data..."):
            numerical_prompt = "Extract all numerical data with context:\n" + "\n\n".join(st.session_state['transcripts'])
            st.session_state['numerical_data'] = get_gemini_response(numerical_prompt)
    if st.session_state['numerical_data']:
        st.markdown(st.session_state['numerical_data'])

    # Create Timeline
    # st.subheader("Create Timeline")
    if st.button("Generate Timeline", key="generate_timeline_button"):
        with st.spinner("Generating timeline..."):
            timeline_prompt = "Extract major events into a chronological timeline:\n" + "\n\n".join(st.session_state['transcripts'])
            st.session_state['timeline'] = get_gemini_response(timeline_prompt)
    if st.session_state['timeline']:
        st.markdown(st.session_state['timeline'])

    # Ask Questions
    st.subheader("Ask Questions")
    user_question = st.text_input("Your Question", placeholder="Ask something about the transcript...")
    if st.button("Ask", key="ask_question_button"):
        if user_question.strip():
            with st.spinner("Generating response..."):
                full_prompt = st.session_state['combined_transcripts'] + "\nQ: " + user_question
                response = get_gemini_response(full_prompt)
            st.session_state['conversation_history'].append((user_question, response))
    
    if st.session_state['conversation_history']:
        for i, (q, a) in enumerate(st.session_state['conversation_history']):
            st.write(f"**Q{i+1}:** {q}")
            st.write(f"**A{i+1}:** {a}")

    # generate pdf 
    if st.button("Add Data to DB"):
        pdf_file = generate_pdf()

        # ✅ Run filldb.py to process the PDF into ChromaDB
        try:
            subprocess.run(["python", "filldb.py", pdf_file], check=True)
            st.success("PDF generated and database updated successfully!")
        except subprocess.CalledProcessError as e:
            st.error(f"Error running filldb.py: {e}")

elif st.session_state.page == "Quiz":
    st.subheader("Quiz Section")
    st.subheader("Take the Quiz")
    if st.button("Generate Quiz", key="generate_quiz_button"):
        combined_transcripts = "\n\n".join(st.session_state['transcripts'])
        quiz_prompt = (
            "Generate 5 MCQs from the transcript. "
            "Each question must have four options in a list and provide the correct answer."
            "Return the response in valid JSON format as a list of dictionaries: "
            "[{'question': str, 'options': list, 'answer': str}]."
        )
        with st.spinner('Generating quiz...'):
            quiz_response = get_gemini_response(combined_transcripts + quiz_prompt)

        try:
            quiz_response = quiz_response.strip().strip("```json").strip("```")
            questions = json.loads(quiz_response)
            st.session_state['mcq_questions'] = questions
        except json.JSONDecodeError:
            st.error("Failed to parse quiz questions.")
    
    if st.session_state.get('mcq_questions'):
        user_answers = {}
        for idx, q in enumerate(st.session_state['mcq_questions']):
            user_answers[f'q{idx}'] = st.radio(q['question'], q['options'], key=f'quiz_q{idx}')

        if st.button("Submit Quiz", key="submit_quiz_button"):
            score = 0
            results = []
            for idx, q in enumerate(st.session_state['mcq_questions']):
                selected = user_answers[f'q{idx}']
                correct = q['answer']
                if selected == correct:
                    score += 1
                results.append(f"**Q{idx+1}:** {q['question']}  \n**Your Answer:** {selected}  \n**Correct Answer:** {correct}\n")

            st.subheader(f"Your Score: {score}/{len(st.session_state['mcq_questions'])}")
            with st.expander("View Answers"):
                for result in results:
                    st.markdown(result)

elif st.session_state.page == "Talk to DB":
    st.subheader("Talk to Your Database 🧠")
    user_query = st.text_input("Ask something from the DB...", placeholder="E.g., What is quantum mechanics?")
    if st.button("Get Answer"):
        if user_query.strip():
            with st.spinner("Searching the database..."):
                # Query ChromaDB
                results = collection.query(query_texts=[user_query], n_results=10)
    
                # Format AI system prompt
                system_prompt = f"""
                You are my second brain. You have summaries about different YouTube videos I watched. 
                Answer my questions based on the data given here. If there is no information that directly answers the question I asked, 
                tell that there is no information on the topic in "the second brain" yet. Use the phrase "second brain"
                Don't make things up on your own and don't give irrelevant information. 
                --------------------
                My Question:
                {user_query}
    
                The data:
                {results['documents']}
                """
    
                # Get AI-generated response
                try:
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    response = model.generate_content(system_prompt)
                    response_text = response.text.strip()
                except Exception as e:
                    response_text = f"Error: {str(e)}"
    
                # Display result
                st.subheader("AI Response")
                st.write(response_text)
        else:
            st.warning("Please enter a question.")