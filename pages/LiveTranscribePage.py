import streamlit as st
import threading
import queue
import os
import json
from modules.mindmap_utils import generate_flowchart_prompt, parse_llm_response

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
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 Summarize the entire transcription"):
            prompt = "Summarize the following transcription briefly."
            summary = get_gemini_response(prompt + "\n\n" + st.session_state['transcription_text'], "gemini-2.0-flash")
            st.markdown(summary)
    
    # Mind Map Section
    st.markdown("---")
    st.markdown("### 🧠 Generate Mind Map")
    
    # Add secondary prompt input
    secondary_prompt = st.text_area(
        "Customize your mind map (optional):",
        placeholder="E.g., 'Focus on key concepts and their relationships', 'Highlight technical terms', etc.",
        key="transcribe_mindmap_secondary_prompt"
    )
    
    if st.button("🗺️ Generate Mind Map", key="generate_mind_map_btn", use_container_width=True):
        with st.spinner("Generating mind map..."):
            # Get the transcription text
            transcription_text = st.session_state.get('transcription_text', '')
            if not transcription_text:
                st.warning("No transcription available to generate mind map")
                st.stop()
            
            # Generate base prompts
            base_flowchart_prompt = generate_flowchart_prompt(transcription_text)
            
            # Add secondary prompt if provided
            if secondary_prompt.strip():
                flowchart_prompt = f"{base_flowchart_prompt}\n\nAdditional Instructions: {secondary_prompt}"
            else:
                flowchart_prompt = base_flowchart_prompt
            
            # Generate and display the flowchart
            mermaid_code = get_gemini_response(flowchart_prompt, "gemini-2.0-flash")
            mermaid_code, _ = parse_llm_response(mermaid_code)
            
            if mermaid_code:
                st.markdown("### 🎨 Generated Mind Map")
                with st.expander("View Flowchart Code"):
                    st.code(mermaid_code, language="mermaid")
                
                # Add Mermaid.js library
                st.markdown(
                    """
                    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
                    <script>
                        mermaid.initialize({ startOnLoad: true });
                    </script>
                    """,
                    unsafe_allow_html=True
                )
                
                # Display the flowchart
                st.markdown(
                    f"""
                    <div class="mermaid">
                    {mermaid_code}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Parse the response to extract the Mermaid code
                mermaid_code, _ = parse_llm_response(mermaid_code)
                
                # Generate mindmap JSON using the LLM
                mind_map_json = get_gemini_response(mindmap_prompt, "gemini-2.0-flash")
                
                try:
                    # Parse the response to extract the mindmap data
                    _, mind_map_data = parse_llm_response(mind_map_json)
                    
                    if mermaid_code:
                        # Display the Mermaid.js flowchart
                        st.markdown("### 🧠 Flowchart Mind Map")
                        
                        # Display the generated Mermaid.js code
                        with st.expander("View Flowchart Code"):
                            st.code(mermaid_code, language="mermaid")
                        
                        # Add Mermaid.js library
                        st.markdown(
                            """
                            <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
                            <script>
                                mermaid.initialize({ startOnLoad: true });
                            </script>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        # Add a download button for the Mermaid code
                        st.download_button(
                            label="💾 Download Flowchart Code",
                            data=mermaid_code,
                            file_name="mindmap.mmd",
                            mime="text/plain",
                            key="download_mindmap"
                        )
                
                except json.JSONDecodeError as e:
                    st.error("Failed to parse mind map data. Here's the raw JSON:")
                    st.code(mind_map_json, language="json")
                    st.error(f"Error: {str(e)}")
                except Exception as e:
                    st.error(f"An error occurred while generating the mind map: {str(e)}")
                    st.code(f"Error details: {str(e)}")

    st.markdown("---")
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
