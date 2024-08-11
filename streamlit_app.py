import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("📄 Document question answering")
st.write(
    "Upload a document below and ask a question about it – GPT will answer! "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Let the user upload multiple files via `st.file_uploader`.
    uploaded_files = st.file_uploader(
        "Upload documents (.txt or .md)", type=("txt", "md"), accept_multiple_files=True
    )

    # Ask the user for a question via `st.text_area`.
    question = st.text_area(
        "Now ask a question about the documents!",
        placeholder="Can you give me a short summary of all the documents?",
        disabled=not uploaded_files,
    )

    if uploaded_files and question:

        # Process the uploaded files and question.
        documents = []
        for uploaded_file in uploaded_files:
            document = uploaded_file.read().decode()
            documents.append(document)
        
        combined_documents = "\n\n---\n\n".join(documents)
        messages = [
            {
                "role": "user",
                "content": f"Here are the documents:\n\n{combined_documents}\n\n---\n\n{question}",
            }
        ]

        # Generate an answer using the OpenAI API.
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream=True,
        )

        # Stream the response to the app using `st.write_stream`.
        st.write_stream(stream)
