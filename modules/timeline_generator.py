import re
import streamlit as st 
from .summarization import get_gemini_response

def extract_timeline(text):
    """Extracts chronological events from text and organizes them as a timeline."""

    response_from_gemini =  get_gemini_response("Extract major events into a chronological timeline:\n" + "\n\n".join(text))
    return response_from_gemini
