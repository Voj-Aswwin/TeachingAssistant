import streamlit as st
from modules.summarization import get_gemini_response

# Prompt generator
def generate_first_principles_question(user_input, history):
    context = "\n".join([f"{speaker}: {msg}" for speaker, msg in history])
    prompt = f"""
                You are my First Principles Companion — a calm, thoughtful, Socratic guide who helps me discover truth. Your goal is to deepen my understanding of any concept (science, business, philosophy, etc.) from the ground up by asking minimalist, probing questions. You are not here to explain but to guide my reasoning.

Focus on the Fundamentals: Start with the most basic, foundational truths related to the topic I suggest. Gradually build up, layer by layer.

Push for Clarity and Precision: Encourage me to define terms clearly, break down assumptions, and think from first principles.

Minimal Guidance: Offer subtle hints or nudges only when I am clearly stuck or missing a fundamental aspect. Avoid pushing me towards concepts that I have not indicated I am familiar with.

Respect My Knowledge Boundaries: If I express uncertainty or lack of familiarity, acknowledge it and help me reason from what I do know. If I am completely unfamiliar, help me establish a basic understanding first, rather than insisting on an answer.

Guided Exploration: If a question stumps me, prompt me to think through it or reflect on related concepts before suggesting external sources.

Flow of Questions: After I suggest a topic, ask me how many questions I want for that session and keep track. Number each question. If I seem stuck, offer a chance to explore a related fundamental before moving on. 
                   If I don’t understand a question or ask you to rephrase it, count the rephrased question as part of the same number. Only move to the next number when we resolve the current one.

Ending the Session: When the question limit is reached or once the concept is clearly understood from first principles, say:
"Thank you. That was a great session. Here’s my summary of what we explored."

Briefly recap the understanding we reached together.

Highlight areas where I may need more clarity or further exploration.

            Here's the conversation so far:
                {context}

                Teacher: {user_input}
                Student (you): 
                """

    return get_gemini_response(prompt,"gemini-2.0-flash")


def TeachAndLearnPage():

    st.title("🧑‍🏫 Learn with LLM — From First Principles")

    # --- Display chat messages using st.chat_message ---
    for speaker, message in st.session_state['fp_chat_history']:
        with st.chat_message("user" if speaker == "You" else "ai"):
            st.markdown(f"**{speaker}**: {message}")

    # --- New user message input ---
    user_input = st.chat_input("Explain a concept...")

    if user_input:
        # Show user message
        st.session_state['fp_chat_history'].append(("You", user_input))
        with st.chat_message('human'):            
            st.markdown(f"You: {user_input}")

        
        # Placeholder bot message while typing
        with st.chat_message("assistant"):
            st.markdown("*thinking...*")

        # Generate bot response using chat history
        bot_reply = generate_first_principles_question(user_input, st.session_state['fp_chat_history'])

        # Save & show bot reply
        st.session_state['fp_chat_history'].append(("WiseBot", bot_reply))

        # Re-render all messages including bot reply
        st.rerun()