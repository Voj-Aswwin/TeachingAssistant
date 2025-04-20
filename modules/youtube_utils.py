import re
from youtube_transcript_api import YouTubeTranscriptApi

def get_video_id(url):
    """Extracts video ID from a YouTube URL."""
    match = re.search(r'v=([a-zA-Z0-9_-]{11})', url)
    return match.group(1) if match else None

def fetch_transcript(url):
    """Fetches the transcript of a given YouTube video."""
    video_id = get_video_id(url)
    if not video_id:
        return None, "Invalid YouTube URL"
    
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id,['en','hi'])
        transcript_text = " ".join([entry['text'] for entry in transcript])
        return transcript_text, None
    except Exception as e:
        return None, f"Error: {str(e)}"
