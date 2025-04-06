import chromadb
import subprocess
import streamlit as st 
from .summarization import get_gemini_response

CHROMA_PATH = "chroma_db"

def connect_db():
    """Connects to the ChromaDB database."""
    return chromadb.PersistentClient(path=CHROMA_PATH).get_or_create_collection(name="youtube_summaries")

def add_to_db(pdf_file_path):
    """Adds new summaries to ChromaDB."""
    # ✅ Run filldb.py to process the PDF into ChromaDB
    try:
        subprocess.run(["python", "filldb.py", pdf_file_path], check=True)
        st.success("PDF generated and database updated successfully!")
    except subprocess.CalledProcessError as e:
        st.error(f"Error running filldb.py: {e}")

def talk_to_db(query):
    # Submits query to DB and retrieves response
    if query.strip():
            with st.spinner("Searching the database..."):
                
                collection = connect_db()
                
                # Query ChromaDB
                results = collection.query(query_texts=[query], n_results=10)

                # Format AI system prompt
                system_prompt = f"""
                You are my second brain. You have summaries about different YouTube videos I watched. 
                Answer my questions based on the data given here. If there is no information that directly answers the question I asked, 
                tell that there is no information on the topic in "the second brain" yet. Use the phrase "second brain"
                Don't make things up on your own and don't give irrelevant information. 
                --------------------
                My Question:
                {query}

                The data:
                {results['documents']}
                """

                # Get AI-generated response
                try:
                    response = get_gemini_response(system_prompt)
                    # print(response)
                    st.session_state['db_conversation'].append((query, response)) 
                    return response
                except Exception as e:
                    response = f"Error: {str(e)}"
    else:
        st.warning("Please enter a question.")

def write_db_conversation_history():
     for i, (q, a) in enumerate(st.session_state['db_conversation']):
            st.write(f"**Q{i+1}:** {q}")
            st.write(f"**A{i+1}:** {a}")        