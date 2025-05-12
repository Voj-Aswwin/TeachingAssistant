import streamlit as st
import threading
import queue
import time
import whisper
import sounddevice as sd
import numpy as np
import wave
import os
import torch

def load_whisper_model():
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = whisper.load_model("base", device=device)
        return model
    except Exception as e:
        st.error(f"Failed to load Whisper model: {e}")
        st.info("Try reinstalling with:")
        st.code("""
pip uninstall torch torchaudio
pip install torch torchaudio
pip install --upgrade openai-whisper
        """)
        return None

def record_audio(audio_queue, status_queue, control_flag):
    sample_rate = 16000
    chunk_duration = 5

    def callback(indata, frames, time_info, status):
        try:
            if status:
                status_queue.put(f"Audio warning: {status}")
            audio_queue.put(indata.copy())
        except Exception as e:
            status_queue.put(f"Callback Error: {str(e)}")

    try:
        with sd.InputStream(samplerate=sample_rate, channels=1, callback=callback):
            while control_flag['running']:
                time.sleep(chunk_duration)
    except Exception as e:
        status_queue.put(f"Stream Error: {str(e)}")

def transcribe_audio_chunks():
    if st.session_state['audio_queue'].empty():
        return

    audio_chunks = []
    while not st.session_state['audio_queue'].empty():
        audio_chunks.append(st.session_state['audio_queue'].get())

    if not audio_chunks:
        return

    audio_data = np.concatenate(audio_chunks)

    # Create recordings folder if needed
    recordings_dir = os.path.join(os.getcwd(), "recordings")
    os.makedirs(recordings_dir, exist_ok=True)

    # Define audio file path
    audio_path = os.path.join(recordings_dir, "live_chunk.wav")

    try:
        # Write the audio file
        with wave.open(audio_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())

        # Transcribe
        result = st.session_state['whisper_model'].transcribe(audio_path, fp16=False, temperature=0, no_speech_threshold=0.4)
        text = result['text'].strip()

        if text:
            # Update live session state
            st.session_state['transcription_text'] += text + " "

    except Exception as e:
        st.session_state['audio_status_queue'].put(f"Transcription error: {str(e)}")

    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path) 