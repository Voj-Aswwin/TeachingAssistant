import streamlit as st
from modules.news_retriever import (
    fetch_all_news,
    generate_news_summary,
    generate_news_chat_response
)

def DailyNewsPage(model_name="gemini-2.0-flash"):
    st.title("Daily News Analysis")
    st.markdown("Analyzing news articles from major sources using Gemini AI.")

    # Initialize session state for news content and summary
    if 'news_content' not in st.session_state:
        st.session_state['news_content'] = None
    if 'news_summary' not in st.session_state:
        st.session_state['news_summary'] = None
    if 'conversation_history' not in st.session_state:
        st.session_state['conversation_history'] = []

    # Fetch and summarize news
    if st.button("📊 Generate News Summary"):
        with st.spinner("Fetching and analyzing news articles..."):
            news_content, errors = fetch_all_news()
            
            if errors:
                for error in errors:
                    st.error(error)
                    
            if news_content:
                st.session_state['news_content'] = news_content
                summary = generate_news_summary(news_content, model_name)
                st.session_state['news_summary'] = summary

    # Display summary
    if st.session_state['news_summary']:
        st.subheader("📝 News Analysis")
        st.markdown(st.session_state['news_summary'])

    # Add a divider between news and chat
    st.markdown("---")
    
    # Chat interface for asking questions
    st.subheader("💬 Chat About the News")
    
    # Display chat history
    for speaker, message in st.session_state['conversation_history']:
        with st.chat_message("user" if speaker == "You" else "ai"):
            st.markdown(f"**{speaker}**: {message}")

    # Chat input
    user_input = st.chat_input("Ask about the news...")

    if user_input and st.session_state['news_content']:
        # Show user message
        st.session_state['conversation_history'].append(("You", user_input))
        with st.chat_message('human'):            
            st.markdown(f"You: {user_input}")

        # Placeholder bot message while thinking
        with st.chat_message("assistant"):
            st.markdown("*thinking...*")

        # Generate response using the news content and chat history
        bot_reply = generate_news_chat_response(
            user_input, 
            st.session_state['conversation_history'],
            st.session_state['news_content'],
            model_name
        )
        
        # Save & show bot reply
        st.session_state['conversation_history'].append(("NewsBot", bot_reply))

        # Re-render all messages including bot reply
        st.rerun()