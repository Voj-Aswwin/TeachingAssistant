import google.generativeai as genai
import os

def get_gemini_response(prompt):
    """Generates a response using Google's Gemini AI."""
    try:
        genai.configure(api_key=os.environ["API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt+" Generate responses only in English")
        return response.text.strip()
    except Exception as e:
        return f"Error generating content: {str(e)}"
