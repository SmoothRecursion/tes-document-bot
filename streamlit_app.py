import streamlit as st
import os
from document_processor import classify_and_process_documents

# Show title and description.
st.title("📄 Automotive Document Question Answering")
st.write(
    "Upload automotive-related documents below and ask a question about them. "
    "The app will classify the documents and provide an answer based on the content."
)

# Check for OpenAI API key in environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    # If not in environment, ask user for their OpenAI API key via `st.text_input`.
    st.write("To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys).")
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.", icon="🗝️")
        st.stop()

# Let the user upload multiple files via `st.file_uploader`.
uploaded_files = st.file_uploader(
    "Upload documents (.txt, .md, or .jsonl)", type=("txt", "md", "jsonl"), accept_multiple_files=True
)

# Ask the user for a question via `st.text_area`.
question = st.text_area(
    "Now ask a question about the documents!",
    placeholder="Can you compare the oil filters mentioned in the documents?",
    disabled=not uploaded_files,
)

if uploaded_files and question:
        # Process the uploaded files
        documents = []
        for uploaded_file in uploaded_files:
            if uploaded_file.name.endswith('.jsonl'):
                import json
                jsonl_content = uploaded_file.read().decode().splitlines()
                documents.extend([json.loads(line)['content'] for line in jsonl_content if line.strip()])
            else:
                documents.append(uploaded_file.read().decode())

        # Use the new document_processor module to classify and answer the question
        with st.spinner("Processing documents and generating answer..."):
            answer = classify_and_process_documents(documents, question, openai_api_key)

        # Display the answer
        st.write("Answer:")
        st.write(answer)
