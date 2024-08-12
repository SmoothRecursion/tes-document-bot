import streamlit as st
import os
from pages import chat, document_upload, search
from components import chatbot, document_viewer
from config import app_config

def main():
    st.set_page_config(
        page_title="Automotive Document Q&A",
        page_icon="📄",
        layout="wide"
    )

    st.title("📄 Automotive Document Question Answering")
    st.write(
        "Upload automotive-related documents, search through them, and ask questions about their content."
    )

    # Sidebar for navigation
    page = st.sidebar.selectbox("Choose a page", ["Upload", "Search", "Chat"])

    if page == "Upload":
        document_upload.render()
    elif page == "Search":
        search.render()
    elif page == "Chat":
        chat.render()

    # Check for OpenAI API key
    if not app_config.OPENAI_API_KEY:
        st.sidebar.warning("OpenAI API key not set. Please set it in the config.")

if __name__ == "__main__":
    main()
