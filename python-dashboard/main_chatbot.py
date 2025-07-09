# app/core.py
import pandas as pd
import streamlit as st
from langchain.agents import AgentType
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_ollama import ChatOllama

def safe_page_config():
    """Handle page config in a way that prevents multiple calls"""
    try:
        st.set_page_config(
            page_title="DF Chat",
            page_icon="💬",
            layout="centered"
        )
    except st.errors.StreamlitAPIException as e:
        if "can only be called once per app" in str(e):
            return
        raise e

def initialize_session_state():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "df" not in st.session_state:
        st.session_state.df = None

def handle_file_upload():
    uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])
    if uploaded_file:
        st.session_state.df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
        st.write("DataFrame Preview:")
        st.dataframe(st.session_state.df.head())

def display_chat_history():
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def handle_user_input(prompt: str):
    try:
        llm = ChatOllama(
            model="gemma:2b",
            temperature=0,
            base_url="http://localhost:8502/"
        )
        
        agent = create_pandas_dataframe_agent(
            llm,
            st.session_state.df,
            verbose=True,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            allow_dangerous_code=True
        )

        response = agent.invoke([
            {"role": "system", "content": "You are a helpful data analysis assistant"},
            *st.session_state.chat_history
        ])
        
        return response["output"]
    except Exception as e:
        return f"Error processing request: {str(e)}"

def chatbot_main():
    """Chatbot component without page config"""
    st.title("🤖 TransBot")
    initialize_session_state()
    handle_file_upload()
    display_chat_history()

    if prompt := st.chat_input("Ask LLM..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        response = handle_user_input(prompt)
        
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
