import chromadb
from openai import OpenAI
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

# setting the environment

CHROMA_PATH = r"chroma_db"

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = chroma_client.get_or_create_collection(name="youtube_summaries")

user_query = input("What do you want to learn today?\n\n")

results = collection.query(
    query_texts=[user_query],
    n_results=10
)

print(results['documents'])
#print(results['metadatas'])

def get_gemini_response(prompt):
    try:
        genai.configure(api_key=os.environ["API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating content: {str(e)}"

system_prompt = f"""
You are my second brain. You have summaries about different YouTube videos I watched. 
Answer my questions based on the data given here. If there is no information that directly answers the question I asked, tell that.  
Don't make things up on your own and don't give irrelevant information. 
--------------------
My Question:
{user_query}

The data:
{results['documents']}
"""


#print(system_prompt)

response = get_gemini_response(system_prompt)

print("\n\n---------------------\n\n")

print(response)