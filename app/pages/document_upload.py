import streamlit as st
import os
import tempfile
from document_processing import batch_processor
from database import mongodb_client

def render():
    st.header("Upload Documents")
    
    uploaded_files = st.file_uploader(
        "Upload documents (.pdf, .jsonl, .csv)", 
        type=["pdf", "jsonl", "csv"], 
        accept_multiple_files=True
    )

    if uploaded_files:
        progress_bar = st.progress(0)
        status_text = st.empty()

        temp_files = []
        file_names = []

        for file in uploaded_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as temp_file:
                chunk_size = 5 * 1024 * 1024  # 5MB chunks
                for chunk in file.chunks(chunk_size):
                    temp_file.write(chunk)
                temp_files.append(temp_file.name)
                file_names.append(file.name)

        try:
            def update_progress(progress):
                progress_bar.progress(progress)
                status_text.text(f"Processing files: {progress:.0%}")

            batch_processor.process_files(temp_files, file_names, update_progress)
            st.success("All files processed successfully!")
        except Exception as e:
            st.error(f"Error processing files: {str(e)}")
        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                os.unlink(temp_file)

        progress_bar.empty()
        status_text.empty()

    # Display uploaded documents
    st.subheader("Uploaded Documents")
    documents = mongodb_client.get_all_documents()
    for doc in documents:
        st.write(f"- {doc['metadata']['file_name']} (Type: {doc['metadata']['file_type']})")
