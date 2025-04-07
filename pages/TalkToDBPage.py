import streamlit as st
from modules.db_utils import talk_to_db, write_db_conversation_history


def TalkToDBPage():
    
    st.title("Talk to Your Database 🧠")

    user_query = st.text_input("Ask something from the DB...", placeholder="E.g., What is quantum mechanics?")
    if st.button("Get Answer"):
       response =  talk_to_db(user_query)

    if st.session_state['db_conversation']:
        write_db_conversation_history() 