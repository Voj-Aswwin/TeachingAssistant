import chromadb
from openai import OpenAI
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

# setting the environment

DATA_PATH = r"data"
CHROMA_PATH = r"chroma_db"

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = chroma_client.get_or_create_collection(name="econ_survey")

user_query = input("What do you want to know about Indian Economy?\n\n")

results = collection.query(
    query_texts=[user_query],
    n_results=1
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

system_prompt = """
You are a helpful assistant. And a economic expert. You answer questions about Indian economy based on the economic survey report published recently. 
But you only answer based on knowledge I'm providing you. You don't use your internal 
knowledge and you don't make things up.
--------------------
The data:
"""+str(results['documents'])+"""
"""

#print(system_prompt)

response = get_gemini_response(system_prompt)

print("\n\n---------------------\n\n")

print(response)