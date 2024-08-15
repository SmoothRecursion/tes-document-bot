import streamlit as st
import sys
import os
import hashlib

from app.views import chat, document_upload, similarity_search

# Authentication functions
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

def main():
    # Initialize session state
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = False
    if 'username' not in st.session_state:
        st.session_state['username'] = ''

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
                st.session_state['username'] = username
                st.rerun()
            else:
                st.sidebar.error("Incorrect Username/Password")
    
    if st.session_state['authentication_status']:
        st.sidebar.success(f"Logged In as {st.session_state['username']}")
        if st.sidebar.button("Logout"):
            st.session_state['authentication_status'] = False
            st.rerun()
        
        st.sidebar.title("Navigation")
        page = st.sidebar.radio("Go to", ["Chat", "Document Upload", "Similarity Search"])

        if page == "Chat":
            chat.render()
        elif page == "Document Upload":
            document_upload.render()
        elif page == "Similarity Search":
            similarity_search.render()

        # Check for OpenAI API key
        # if not app_config.OPENAI_API_KEY:
        #     st.sidebar.warning("OpenAI API key not set. Please set it in the config.")
    else:
        st.title("Please login to access the application")

if __name__ == "__main__":
    main()
