import streamlit as st
import threading
import queue
import os

from modules.summarization import get_gemini_response
from modules.live_transcriber import load_whisper_model, record_audio, transcribe_audio_chunks

# Main Streamlit Page
def LiveTranscribePage():

    st.title("🎤 Voice Transcription & Chat")

    # --- Session State Init ---
    for key, default in {
        'whisper_model': None,
        'audio_queue': None,
        'audio_status_queue': None,
        'transcription_text': "",
        'conversation_history': [],
        'is_recording': False,
        'recording_control_flag': None,
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

    if st.session_state['audio_queue'] is None:
        st.session_state['audio_queue'] = queue.Queue()
    if st.session_state['audio_status_queue'] is None:
        st.session_state['audio_status_queue'] = queue.Queue()
    if st.session_state['recording_control_flag'] is None:
        st.session_state['recording_control_flag'] = {'running': False}

    # --- Whisper Model Load ---
    if st.session_state['whisper_model'] is None:
        with st.spinner("Loading Whisper model..."):
            os.environ['CURL_CA_BUNDLE'] = ""
            st.session_state['whisper_model'] = load_whisper_model()
            if st.session_state['whisper_model'] is None:
                return

    # --- Recording Controls ---
    start = st.button("🎙️ Start Recording")
    stop = st.button("⏹️ Stop Recording")

    if start and not st.session_state['is_recording']:
        st.session_state['is_recording'] = True
        st.session_state['recording_control_flag']['running'] = True
        threading.Thread(
            target=record_audio,
            args=(
                st.session_state['audio_queue'],
                st.session_state['audio_status_queue'],
                st.session_state['recording_control_flag'],
            ),
            daemon=True
        ).start()

    if stop and st.session_state['is_recording']:
        st.session_state['is_recording'] = False
        st.session_state['recording_control_flag']['running'] = False

    # --- Visual Mic Status Indicator ---
    mic_status = "🔴 Mic is LIVE" if st.session_state['is_recording'] else "⚫️ Mic is OFF"
    mic_color = "#ff4b4b" if st.session_state['is_recording'] else "#AAAAAA"

    st.markdown(
        f"""
        <div style='
            padding: 0.5rem 1rem;
            margin-top: 1rem;
            border-radius: 0.5rem;
            background-color: {mic_color};
            color: white;
            width: fit-content;
            font-weight: bold;
            '>{mic_status}</div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")
    # --- Process incoming audio for transcription ---
    transcribe_audio_chunks()

    # --- Display any recording errors ---
    while not st.session_state['audio_status_queue'].empty():
        st.warning(st.session_state['audio_status_queue'].get())

    # --- Summarize the transcription ---

    if(st.button("Summarize the entire transcription")):
        prompt = "Summarize the following transcription briefly."
        summary = get_gemini_response(prompt + "\n\n" + st.session_state['transcription_text'], "gemini-2.0-flash")
        st.markdown(summary)

    # --- Chat Interface ---
    st.subheader("💬 Chat with Transcribed Audio")

    for speaker, message in st.session_state['conversation_history']:
        with st.chat_message("user" if speaker == "You" else "ai"):
            st.markdown(f"**{speaker}**: {message}")

    user_input = st.chat_input("Ask something based on what you've said...")

    if user_input and st.session_state['transcription_text']:
        st.session_state['conversation_history'].append(("You", user_input))
        with st.chat_message('user'):            
            st.markdown(f"**You**: {user_input}")

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                prompt = f"""Answer this based only on the following transcription. 
If you don't find the answer in the transcript, say that clearly.

Transcription:
{st.session_state['transcription_text']}

User Query:
{user_input}
"""
                response = get_gemini_response(prompt, "gemini-2.0-flash")
                st.markdown(response)
                st.session_state['conversation_history'].append(("Assistant", response))
