import streamlit as st
from app.backend.database.mongodb_client import AtlasClient

def render():
    st.title("Similarity Search")

    # Text input for the query
    query = st.text_input("Enter your search query:")

    # Number input for k (number of results)
    k = st.number_input("Number of results to return:", min_value=1, max_value=20, value=5)

    if st.button("Search"):
        if query:
            # Initialize AtlasClient
            atlas_client = AtlasClient()

            # Perform similarity search
            results = atlas_client.similarity_search(query, k=k)

            # Display results
            st.subheader("Search Results:")
            for i, doc in enumerate(results, 1):
                st.markdown(f"**Result {i}:**")
                st.write(f"Content: {doc.page_content}")
                st.markdown("---")
        else:
            st.warning("Please enter a search query.")
