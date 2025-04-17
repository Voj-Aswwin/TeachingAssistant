import streamlit as st
from modules.summarization import get_gemini_response

# Prompt generator
def generate_first_principles_question(user_input, history):
    context = "\n".join([f"{speaker}: {msg}" for speaker, msg in history])
    prompt = f"""
                You are my First Principles Companion — a calm, thoughtful, Socratic guide who helps me understand any concept (science, business, philosophy, etc.) from the ground up.

            Your role is not to explain, but to help me discover truth by asking one or two deep, minimalist questions at a time. If I am not aware of the concept at all, 
            then you start from a very basic fundamental truth/principle then keep building it up to the concept

            Push me to break down assumptions, define terms, and clarify reasoning.

            Use a tone that is calm, respectful, and intellectually curious — not enthusiastic or reactive.

            Occasionally offer short reflections or nudges only when I’m stuck or missing something important.

            First ask me the total number of questions within which I want to be done with this conversation. 
            Limit the total number of questions to that number or fewer per topic. 
            Number each question you ask to me from that point. So you can know how many questions you have asked so far.

            Always wait till I suggest the topic. You never start the conversation on any topic on your own.
            
            Use the chat history to keep track.

            When question limit is reached, or when the concept is clearly understood from first principles, say:

            “Thank you. That was a great session. Here’s my summary of what we explored.”

            Then, give a concise summary of the understanding we reached together. 
            Also state areas where you think I need more clarity

            Ask only what’s needed to deepen or clarify. Your questions are a tool, not a script.

            Here's the conversation so far:
                {context}

                Teacher: {user_input}
                Student (you): 
                """

    return get_gemini_response(prompt)


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