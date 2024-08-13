import streamlit as st
from backend.ai_models import model_loader
from backend.database.mongodb_client import AtlasClient

def render():
    st.header("Chat with Your Documents")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("What would you like to know about the documents?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Thinking..."):
            # Get the CRAG model
            crag_model = model_loader.get_crag_model()
            
            # Fetch relevant documents from the database
            db_client = AtlasClient()
            documents = db_client.find("documents", limit=10)  # Adjust limit as needed
            
            # Prepare the context for the model
            context = "\n".join([doc.get('content', '') for doc in documents])
            
            # Generate response using the CRAG model
            response = crag_model.generate(context, prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Add a button to clear chat history
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.experimental_rerun()
