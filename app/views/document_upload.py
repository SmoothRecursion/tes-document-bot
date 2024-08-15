import streamlit as st
import os
import tempfile
from ..backend import document_processing

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
                temp_file.write(file.read())
                temp_files.append(temp_file.name)
                file_names.append(file.name)

        try:
            def update_progress(progress):
                progress_bar.progress(progress)
                status_text.text(f"Processing files: {progress:.0%}")

            document_processing.batch_processor.process_files(file_paths=temp_files, file_names=file_names, progress_callback=update_progress)
            st.success("All files processed successfully!")
        except Exception as e:
            st.error(f"Error processing files: {str(e)}")
            st.exception(e)
        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                os.unlink(temp_file)

        progress_bar.empty()
        status_text.empty()

    # Display uploaded documents
    st.subheader("Uploaded Documents")
