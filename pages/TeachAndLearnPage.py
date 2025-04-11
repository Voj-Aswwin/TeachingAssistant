import streamlit as st
from modules.summarization import get_gemini_response

# Prompt generator
def generate_first_principles_question(user_input, history):
    context = "\n".join([f"{speaker}: {msg}" for speaker, msg in history])
    prompt = f"""
                You are a thoughtful student learning through the method of first principles.

                A teacher is explaining a concept to you. Your goal is to understand it deeply by asking one or two simple but deep questions at a time that break the explanation down to its fundamental parts.

                Use a calm, inquisitive tone.

                Address the teacher respectfully as "Professor" or "Sir."

                Acknowledge when you understand something before moving on.

                Always return to any questions that remain unresolved.

                Focus on deep questions like:

                - “Why is that true?”
                  “What do you mean by that?”
                   “What are the assumptions behind that?”
                   “How do we know that’s the case?”

                Limit yourself to a maximum of 10 questions per topic.
                Use the chat history to keep track. When you believe you've understood the concept from first principles, say:

                “Thank you, Professor. That was a great session. Here’s my summary of what I learned today.”

                Then clearly summarize your understanding of the concept.

                Avoid excessive enthusiasm. Be intellectually curious and precise, not excitable.

                Here's the conversation so far:
                {context}

                Teacher: {user_input}
                Student (you): 
                """

    return get_gemini_response(prompt)


def TeachAndLearnPage():

    st.title("🧑‍🏫 Teach to Gemini — From First Principles")

    # --- Display chat messages using st.chat_message ---
    for speaker, message in st.session_state['fp_chat_history']:
        with st.chat_message("user" if speaker == "You" else "assistant"):
            st.markdown(f"**{speaker}**: {message}")

    # --- New user message input ---
    user_input = st.chat_input("Explain a concept...")

    if user_input:
        # Show user message
        st.session_state['fp_chat_history'].append(("You", user_input))

        # Placeholder bot message while typing
        with st.chat_message("assistant"):
            st.markdown("*typing...*")

        # Generate bot response using chat history
        bot_reply = generate_first_principles_question(user_input, st.session_state['fp_chat_history'])

        # Save & show bot reply
        st.session_state['fp_chat_history'].append(("CuriousBot", bot_reply))

        # Re-render all messages including bot reply
        st.rerun()