import streamlit as st
import sys
import os

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from pages import chat, document_upload
# from config import app_config

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
    elif page == "Chat":
        chat.render()

    # Check for OpenAI API key
    # if not app_config.OPENAI_API_KEY:
    #     st.sidebar.warning("OpenAI API key not set. Please set it in the config.")

if __name__ == "__main__":
    main()
