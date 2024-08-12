import streamlit as st
import os
import tempfile
from backend.document_processing import batch_processor
from backend.database import mongodb_client

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

        for i, file in enumerate(uploaded_files):
            status_text.text(f"Processing file {i+1} of {len(uploaded_files)}: {file.name}")
            
            # Create a temporary file to store the uploaded content
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as temp_file:
                # Stream the file content in chunks
                chunk_size = 5 * 1024 * 1024  # 5MB chunks
                file_size = file.size
                bytes_read = 0

                for chunk in file.chunks(chunk_size):
                    temp_file.write(chunk)
                    bytes_read += len(chunk)
                    progress = bytes_read / file_size
                    progress_bar.progress(progress)

            # Process the temporary file
            try:
                batch_processor.process_file(temp_file.name, file.name)
                st.success(f"Successfully processed {file.name}")
            except Exception as e:
                st.error(f"Error processing {file.name}: {str(e)}")
            finally:
                # Clean up the temporary file
                os.unlink(temp_file.name)

            progress_bar.progress((i + 1) / len(uploaded_files))

        status_text.text("All files processed!")
        progress_bar.empty()

    # Display uploaded documents
    st.subheader("Uploaded Documents")
    documents = mongodb_client.get_all_documents()
    for doc in documents:
        st.write(f"- {doc['filename']} (Type: {doc['file_type']})")
