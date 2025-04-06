import re
import streamlit as st
from .summarization import get_gemini_response

def extract_numerical_data(transcript):
    """Extracts numerical values (years, percentages, prices, etc.) from a given text."""
   
    response_from_Gemini = get_gemini_response("Extract all numerical data with context:\n" + "\n\n".join(transcript))         
    return response_from_Gemini
  

