import re
from youtube_transcript_api import YouTubeTranscriptApi
from datetime import datetime, timedelta
from yt_dlp import YoutubeDL

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
        transcript = YouTubeTranscriptApi.get_transcript(video_id,['en','hi','ta'])
        transcript_text = " ".join([entry['text'] for entry in transcript])
        return transcript_text, None
    except Exception as e:
        return None, f"Error: {str(e)}"

def get_recent_videos_from_playlists(playlists):
    """
    Returns URLs of the most recent video from each playlist
    if uploaded today or yesterday.
    """
    recent_videos = []
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True
    }

    with YoutubeDL(ydl_opts) as ydl:
        for playlist_url in playlists:
            try:
                info = ydl.extract_info(playlist_url, download=False)
                entries = info.get('entries', [])
                if not entries:
                    continue

                latest_video = entries[0]  # Most recent (top of the playlist)
                video_url = f"https://www.youtube.com/watch?v={latest_video['id']}"

                # Now fetch full metadata for that video
                video_info = ydl.extract_info(video_url, download=False)
                upload_date_str = video_info.get('upload_date')  # format: YYYYMMDD

                if not upload_date_str:
                    continue

                upload_date = datetime.strptime(upload_date_str, "%Y%m%d").date()
                if upload_date in {today, yesterday}:
                    recent_videos.append(video_url)

            except Exception as e:
                print(f"Error processing playlist {playlist_url}: {e}")

    return recent_videos
