import streamlit as st
import sys
import os

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app.pages import chat, document_upload

def main():
    st.set_page_config(
        page_title="Automotive Document QA",
        page_icon="🚗",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items=None
    )

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Chat", "Document Upload"])

    if page == "Home":
        st.title("📄 Automotive Document Question Answering")
        st.write(
            "Upload automotive-related documents, search through them, and ask questions about their content."
        )
    elif page == "Chat":
        chat.render()
    elif page == "Document Upload":
        document_upload.render()

    # Check for OpenAI API key
    # if not app_config.OPENAI_API_KEY:
    #     st.sidebar.warning("OpenAI API key not set. Please set it in the config.")

if __name__ == "__main__":
    main()
