import google.generativeai as genai
import os

def get_gemini_response(prompt, model_name="gemini-2.5-pro-exp-03-25"):
    """Generates a response using Google's Gemini AI.
    
    Args:
        prompt (str): The prompt to generate a response for
        model_name (str): The name of the Gemini model to use. Defaults to "gemini-2.5-pro-exp-03-25"
    
    Returns:
        str: The generated response text
    """
    try:
        genai.configure(api_key=os.environ["API_KEY"])
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt+" Generate responses only in English")
        return response.text.strip()
    except Exception as e:
        return f"Error generating content: {str(e)}"
