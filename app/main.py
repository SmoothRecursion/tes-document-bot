import streamlit as st
import sys
import os
import hashlib

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app.views import chat, document_upload

# Authentication functions
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# Initialize session state
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = False

def main():
    st.set_page_config(
        page_title="Automotive Document QA",
        page_icon="🚗",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items=None
    )

    # Authentication
    if not st.session_state['authentication_status']:
        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password", type='password')
        if st.sidebar.button("Login"):
            # Here you should check against your user database
            # For this example, we'll use a hardcoded username and password
            if username == "admin" and check_hashes(password, make_hashes("password")):
                st.session_state['authentication_status'] = True
                st.rerun()
            else:
                st.sidebar.error("Incorrect Username/Password")
    
    if st.session_state['authentication_status']:
        st.sidebar.success("Logged In as {}".format(username))
        if st.sidebar.button("Logout"):
            st.session_state['authentication_status'] = False
            st.rerun()
        
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
    else:
        st.title("Please login to access the application")

if __name__ == "__main__":
    main()
