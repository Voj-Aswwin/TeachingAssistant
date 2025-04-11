import chromadb
import subprocess
import streamlit as st 
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .summarization import get_gemini_response

CHROMA_PATH = "chroma_db"

def connect_db():
    #Connects to the ChromaDB database
    collection =  chromadb.PersistentClient(path=CHROMA_PATH)
    return collection.get_or_create_collection(name="youtube_summaries")

def add_pdf_documents_to_db(pdf_file_path):
     
     #Processes and adds new documents from PDFs into ChromaDB.

     chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
     collection = chroma_client.get_or_create_collection(name="youtube_summaries")
     
     # loading the document
     loader = PyPDFDirectoryLoader("data")
     raw_documents = loader.load()
     
     # splitting the document
     text_splitter = RecursiveCharacterTextSplitter(
         chunk_size=300,
         chunk_overlap=100,
         length_function=len,
         is_separator_regex=False,
     )
     
     chunks = text_splitter.split_documents(raw_documents)
     
     # Get existing IDs to prevent overwriting
     existing_data = collection.get()
     existing_ids = set(existing_data["ids"]) if existing_data["ids"] else set()
     
     # preparing to be added in chromadb
     documents = []
     metadata = []
     ids = []
     
     # Start ID numbering after the last existing ID
     i = len(existing_ids)
     
     for chunk in chunks:
         new_id = "ID" + str(i)
     
         # Avoid ID duplication
         while new_id in existing_ids:
             i += 1
             new_id = "ID" + str(i)
     
         documents.append(chunk.page_content)
         ids.append(new_id)
         metadata.append(chunk.metadata)
     
         i += 1
     
     print(documents,metadata,ids)

     # adding to chromadb
     collection.upsert(
         documents=documents,
         metadatas=metadata,
         ids=ids
     )

     return len(documents)

def add_to_db(pdf_file_path):
   
   #Loads PDF summaries from data folder and adds them to ChromaDB.

    try:
        new_doc_count = add_pdf_documents_to_db(pdf_file_path)
        st.session_state['collection'] = connect_db()
        st.success(f"{new_doc_count} new documents added to the database successfully!")
    except Exception as e:
        st.error(f"Error updating database: {e}")

def talk_to_db(query):
    # Submits query to DB and retrieves response
    if query.strip():
            with st.spinner(" 🧠 Thinking..."):
                
                collection = connect_db()
                
                # Query ChromaDB
                results = collection.query(query_texts=[query], n_results=10)

                # Format AI system prompt
                system_prompt = f"""
                You are my second brain. You are an extension of me. 
                You have summaries about different YouTube videos I watched. 
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