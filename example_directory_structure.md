chatbot_project/
│
├── app/
│   ├── main.py
│   ├── pages/
│   │   ├── chat.py
│   │   ├── document_upload.py
│   │   └── search.py
│   └── components/
│       ├── chatbot.py
│       └── document_viewer.py
│
├── backend/
│   ├── database/
│   │   ├── mongodb_client.py
│   │   └── models.py
│   ├── document_processing/
│   │   ├── pdf_processor.py
│   │   ├── jsonl_processor.py
│   │   └── batch_processor.py
│   ├── search/
│   │   ├── semantic_search.py
│   │   └── filtering.py
│   ├── ai_models/
│   │   ├── response_generator.py
│   │   ├── function_caller.py
│   │   └── model_loader.py
│   └── utils/
│       ├── text_splitter.py
│       └── metadata_extractor.py
│
├── config/
│   ├── app_config.py
│   └── logging_config.py
│
├── tests/
│   ├── test_document_processing.py
│   ├── test_search.py
│   ├── test_database.py
│   └── test_ai_models.py
│
├── requirements.txt
└── README.md
# File Contents Overview

## app/

### main.py
- Set up the main Streamlit application
- Configure page layout and navigation
- Import and render other pages/components

### pages/chat.py
- Implement the chat interface
- Handle user input and display bot responses
- Integrate with backend chatbot component

### pages/document_upload.py
- Create file upload interface for PDFs and JSONL files
- Trigger document processing on upload
- Display upload status and processing results

### pages/search.py
- Implement search interface with filters
- Connect to backend search functionality
- Display search results

### components/chatbot.py
- Create a reusable Streamlit component for the chatbot interface
- Handle chat history and message display

### components/document_viewer.py
- Implement a component to view processed documents
- Display document metadata and content snippets

## backend/

### database/mongodb_client.py
- Set up MongoDB connection
- Implement CRUD operations for documents and metadata

### database/models.py
- Define data models for documents, metadata, and chat history

### document_processing/pdf_processor.py
- Implement PDF parsing and text extraction
- Handle PDF-specific metadata extraction

### document_processing/jsonl_processor.py
- Implement JSONL parsing and data extraction
- Handle JSONL-specific metadata extraction

### document_processing/batch_processor.py
- Implement batch processing logic for large documents
- Manage processing queue and status updates

### search/semantic_search.py
- Implement semantic search functionality
- Integrate with a vector database or similarity search library

### search/filtering.py
- Implement metadata-based filtering
- Combine filtering with semantic search results

### utils/text_splitter.py
- Implement text splitting algorithms
- Handle different splitting strategies (by sentence, paragraph, etc.)

### utils/metadata_extractor.py
- Implement generic metadata extraction
- Handle different metadata fields and formats

### ai_models/response_generator.py

- Implement interface with language model API or local model
- Handle context management for coherent conversations
- Generate responses based on user input and relevant document content

### ai_models/function_caller.py

- Define a set of functions that the AI can call
- Implement logic for parsing AI function calls and executing appropriate actions
- Handle error cases and unexpected inputs in function calls

### ai_models/model_loader.py

- Manage initialization and loading of AI models
- Implement model switching logic if multiple models are used
- Handle model-specific configurations and optimizations

## config/

### app_config.py
- Store application-wide configuration
- Include settings for Streamlit, MongoDB, and processing options

### logging_config.py
- Configure logging for the application
- Set up different log levels and outputs

## tests/

### test_document_processing.py
- Unit tests for PDF and JSONL processors
- Test batch processing functionality

### test_search.py
- Unit tests for semantic search and filtering
- Test search result accuracy and performance

### test_database.py
- Unit tests for MongoDB operations
- Test data model integrity and CRUD operations

## requirements.txt
- List all Python package dependencies with versions

## README.md
- Provide project overview and setup instructions
- Include usage guidelines and contribution information