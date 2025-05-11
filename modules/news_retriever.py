import requests
from bs4 import BeautifulSoup
from .summarization import get_gemini_response

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
        "https://www.bbc.com/news",
        "https://www.theguardian.com/international",
        "https://www.aljazeera.com/news",
        "https://www.nytimes.com",
        "https://www.firstpost.com/",
        "https://inc42.com/",
        "https://www.livemint.com/",
        "https://www.thehindu.com/",
        "https://www.thehindu.com/news/national/",
        "https://www.thehindu.com/news/international/"
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
    summary_prompt = """Analyze these news articles and provide:
    1. A comprehensive summary of the 15 main stories
    2. Key points and important details of each story in about 60 words
    3. Any notable trends or patterns
    4. Potential implications or future developments
    
    Format the response with clear headers and bullet points."""
    
    return get_gemini_response(news_content + summary_prompt, model_name)

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