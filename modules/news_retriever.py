import requests
from bs4 import BeautifulSoup
from .summarization import get_gemini_response
from .youtube_utils import fetch_transcript, get_recent_videos_from_playlists

def fetch_news_content(url):
    """Fetches and extracts content from a news URL.
    
    Args:
        url (str): The URL of the news article to fetch
        
    Returns:
        tuple: (content, error) where content is the extracted text content or None,
               and error is an error message or None
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove unwanted elements
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
            tag.decompose()
            
        # Extract text content
        text = soup.get_text(separator="\n")
        clean_lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(clean_lines), None
    except Exception as e:
        return None, f"Failed to fetch content from {url}: {e}"

def get_news_urls():
    """Returns the list of news URLs to fetch from.
    
    Returns:
        list: List of news URLs
    """
    return [
        "https://www.thehindu.com/news/national/"
        # "https://www.theguardian.com/international",
        # "https://www.aljazeera.com/news",
        # "https://www.nytimes.com",
        # "https://www.firstpost.com/",
        # "https://entrackr.com/",
        # "https://www.livemint.com/",
        # "https://www.thehindu.com/",
        # "https://www.thehindu.com/news/national/",
        # "https://www.thehindu.com/news/international/",
        # "https://techcrunch.com/",
        # "https://www.techcrunch.com/"
    ]

def fetch_all_news():
    """Fetches content from all configured news URLs.
    
    Returns:
        tuple: (combined_content, errors) where combined_content is the concatenated text
               from all successfully fetched URLs, and errors is a list of error messages
    """
    all_content = []
    errors = []
    
    for url in get_news_urls():
        content, error = fetch_news_content(url)
        if content:
            all_content.append(content)
        if error:
            errors.append(error)
            
    return "\n\n".join(all_content) if all_content else None, errors

def generate_news_summary(news_content, model_name="gemini-2.0-flash"):
    """Generates a summary of the news content using Gemini.
    
    Args:
        news_content (str): The combined news content to summarize
        model_name (str): The name of the Gemini model to use
        
    Returns:
        str: The generated summary
    """
    summary_prompt = """
    Given the news stories, help me identify the underlying mental models, economic 
    and psychological incentives, power dynamics, technological trends, and long-term implications. 
    Avoid summarising the headlines—focus instead on what's truly driving these events.

    - What forces (economic, societal, political, technological) are at play beneath the surface?
    - Who benefits, who loses, and what trade-offs are being made?
    - What mental models or cognitive biases explain this behaviour or decision?
    - How might this evolve over 1, 3, and 10 years? What are the second- or third-order effects?
    - Are there connections or patterns across multiple stories?

    Apply the following modifiers depending on the type of story:

    - Startup or Tech Business News:
        "What's the core moat or edge here—tech, distribution, or brand? Is this solving a vitamin problem or a painkiller-level problem? 
        Who loses market share or leverage if this works?"
    - Policy or Regulatory News:
        "What behaviour is the policy attempting to shape or curb? Whose power is being protected or threatened? Are there unintended consequences waiting to happen?"
    - Consumer Trends:
        "What fear, desire, or aspiration is this trend tapping into? What does this say about shifting values or identity signals in the culture?"
    - International/Geopolitical News:
        "What are the hidden goals—economic access, soft power, resource control, strategic alliances? What game theory principles are at play?"
      Finish by listing 1–3 mental models or frameworks that best explain the behaviours, systems, or decisions reflected in the news.
      
      """
    
    return get_gemini_response(news_content + summary_prompt)

def generate_news_chat_response(user_input, history, news_content, model_name="gemini-2.0-flash"):
    """Generates a chat response about the news content.
    
    Args:
        user_input (str): The user's message
        history (list): List of (speaker, message) tuples representing chat history
        news_content (str): The news content to reference
        model_name (str): The name of the Gemini model to use
        
    Returns:
        str: The generated response
    """
    context = "\n".join([f"{speaker}: {msg}" for speaker, msg in history])
    prompt = f"""You are a knowledgeable news analyst assistant. You have access to the following news articles:

{news_content}

Your role is to:
1. Answer questions about the news articles in a clear and concise manner
2. Provide context and background information when relevant
3. Connect different news stories when appropriate
4. Be factual and objective in your responses
5. If asked about topics not covered in the news articles, politely indicate that you can only discuss the provided news content

Use a professional and informative tone. Keep responses focused and relevant to the news content provided.

Here's the conversation so far:
{context}

User: {user_input}
Assistant: """

    return get_gemini_response(prompt, model_name)

def generate_youtube_news_data():
    """
    Fetches transcripts from recent YouTube videos from playlists,
    combines them into a super transcript, and uses Gemini to extract 
    and categorize news snippets from it.
    
    Returns:
        dict: News data in the format {"National": [{title, summary}, ...], 
                                      "World": [{title, summary}, ...],
                                      "Sports": [{title, summary}, ...],
                                      "Business": [{title, summary}, ...],
                                      "Miscellaneous": [{title, summary}, ...]}
    """
    # List of YouTube news playlists to fetch from
    playlists = [
        "https://www.youtube.com/playlist?list=PL2A-r6Y8n7prKj5U2oKXAcUM7sQAMT5MF", # Mint Top of the morning
        "https://www.youtube.com/playlist?list=PLEVkQGIATCXITdX_woAg7DaAm5QVW0aEb" # firspost Vantage podcast
    ]
    
    # Get recent videos from playlists
    youtube_urls =  get_recent_videos_from_playlists(playlists)
    
    
    # Collect all transcripts into one super transcript
    all_transcripts = []
    for url in youtube_urls:
        transcript, error = fetch_transcript(url)
        if error or not transcript:
            continue
        all_transcripts.append(transcript)
    
    super_transcript = "\n\n---\n\n".join(all_transcripts)
    
    if not super_transcript:
        # Fallback to mock data if no transcripts were retrieved
        return {
            "National": [{"title": "Failed to fetch news", "summary": "Could not retrieve transcripts from YouTube."}],
            "World": [{"title": "Failed to fetch news", "summary": "Could not retrieve transcripts from YouTube."}],
            "Sports": [{"title": "Failed to fetch news", "summary": "Could not retrieve transcripts from YouTube."}],
            "Business": [{"title": "Failed to fetch news", "summary": "Could not retrieve transcripts from YouTube."}],
            "Miscellaneous": [{"title": "Failed to fetch news", "summary": "Could not retrieve transcripts from YouTube."}]
        }
    
    # Prompt for Gemini to extract and categorize news snippets
    prompt = f"""
    I have a collection of news transcripts. Extract at least 5 different news stories from these transcripts.
    
    For each news story:
    1. Identify if it belongs to "National" (Indian news), "World" (international news), "Sports", "Business", or "Miscellaneous" (anything else)
    2. Create a short, catchy title (5-7 words)
    3. Write a concise summary (80-100 words)
    
    Format your response as a JSON object matching this structure exactly:
    {{
        "National": [
            {{"title": "Short Title Here", "summary": "80-100 word summary here..."}},
            ...more items...
        ],
        "World": [
            {{"title": "Short Title Here", "summary": "80-100 word summary here..."}},
            ...more items...
        ],
        "Sports": [
            {{"title": "Short Title Here", "summary": "80-100 word summary here..."}},
            ...more items...
        ],
        "Business": [
            {{"title": "Short Title Here", "summary": "80-100 word summary here..."}},
            ...more items...
        ],  
        "Miscellaneous": [
            {{"title": "Short Title Here", "summary": "80-100 word summary here..."}},
            ...more items...
        ]
    }}
    
    The summary should be factual and engaging. Rework on spellings of names and places if found to be wrong.
    
    Here are the transcripts:
    
    {super_transcript}
    """
    
    # Get response from Gemini
    response = get_gemini_response(prompt,"gemini-2.0-flash")
    
    # Process the response to extract the JSON
    try:
        import json
        import re
        
        # Find JSON object in response (in case there's additional text)
        json_match = re.search(r'({[\s\S]*})', response)
        if json_match:
            json_str = json_match.group(1)
            news_data = json.loads(json_str)
            
            # Ensure all required categories exist
            for category in ["National", "World", "Sports", "Business", "Miscellaneous"]:
                if category not in news_data:
                    news_data[category] = []
                    
            return news_data
        
    except Exception as e:
        print(f"Error processing Gemini response: {e}")
    
    # Fallback to basic structure if JSON parsing fails
    return {
        "National": [{"title": "Error Processing News", "summary": "There was an error processing the news data. Please try again later."}],
        "World": [{"title": "Error Processing News", "summary": "There was an error processing the news data. Please try again later."}],
        "Sports": [{"title": "Error Processing News", "summary": "There was an error processing the news data. Please try again later."}],
        "Business": [{"title": "Error Processing News", "summary": "There was an error processing the news data. Please try again later."}],
        "Miscellaneous": [{"title": "Error Processing News", "summary": "There was an error processing the news data. Please try again later."}]
    } 