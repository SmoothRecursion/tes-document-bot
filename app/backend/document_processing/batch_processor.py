import os
from typing import List, Dict, Any, Generator
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue, Empty
from langchain_core import Document
from backend.document_processing import jsonl_processor, csv_processor
from backend.database.mongodb_client import AtlasClient
from backend.ai_models.model_loader import load_embedding_model, get_crag_model
from backend.utils.text_splitter import split_text
from backend.utils.metadata_extractor import extract_metadata

def process_file(file_path: str, file_name: str) -> Generator[Dict[str, Any], None, None]:
    """Process a single file and yield its metadata and content."""
    file_type = os.path.splitext(file_name)[1].lower()
    
    if file_type in ['.jsonl', '.json']:
        processor = jsonl_processor.process_jsonl
    elif file_type == '.csv':
        processor = csv_processor.process_csv
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
    
    for content in processor(file_path):
        if isinstance(content, dict):
            metadata = content
            content = csv_processor.format_for_similarity(content)
        else:
            metadata = {}
            content = str(content)  # Ensure content is a string
        
        # Add file-specific metadata
        metadata['file_name'] = file_name
        metadata['file_type'] = file_type
        
        # Extract additional metadata
        additional_metadata = extract_metadata(content)
        metadata.update(additional_metadata)
        
        yield {'content': content, 'metadata': metadata}

def create_embeddings(texts: List[str], model_name: str = "openai", progress_callback=None) -> List[List[float]]:
    """Create embeddings for a list of texts."""
    model = load_embedding_model(model_name)
    embeddings = []
    total = len(texts)
    
    for i, text in enumerate(texts):
        embedding = model.embed_query(text)
        embeddings.append(embedding)
        if progress_callback:
            progress_callback(i + 1, total)
    
    return embeddings

def batch_process_file(file_path: str, file_name: str, embedding_model: str = "openai", progress_callback=None, atlas_client: AtlasClient = None) -> None:
    if atlas_client is None:
        atlas_client = AtlasClient()
    """Process a file in batches, create embeddings, and store in the database."""
    processed_data_generator = process_file(file_path, file_name)
    
    chunk_index = 0
    total_progress = 0
    for processed_data in processed_data_generator:
        content = processed_data['content']
        metadata = processed_data['metadata']
        
        chunks = split_text(content, chunk_size=1000, chunk_overlap=100)
        
        def embedding_progress(current, total):
            nonlocal total_progress
            total_progress = current / total / 2  # First half of progress
            if progress_callback:
                progress_callback(total_progress)
        
        embeddings = create_embeddings(chunks, model_name=embedding_model, progress_callback=embedding_progress)
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            document = {
                'text': chunk,
                'embedding': embedding,
                'metadata': metadata,
                'chunk_index': chunk_index + i,
            }
            document = Document(page_content=document['text'], metadata=document['metadata'])
            atlas_client.insert_document("documents", document)
            total_progress = 0.5 + (i + 1) / len(chunks) / 2  # Second half of progress
            if progress_callback:
                progress_callback(total_progress)
        
        chunk_index += len(chunks)

def process_files(file_paths: List[str], file_names: List[str], embedding_model: str = "openai", progress_callback=None, atlas_client: AtlasClient = None) -> None:
    if atlas_client is None:
        atlas_client = AtlasClient()
    """Process multiple files concurrently."""
    progress_queue = Queue()
    
    def queue_progress_callback(progress):
        progress_queue.put(progress)
    
    with ThreadPoolExecutor() as executor:
        futures = []
        for file_path, file_name in zip(file_paths, file_names):
            future = executor.submit(batch_process_file, file_path, file_name, embedding_model, queue_progress_callback, atlas_client)
            futures.append(future)
        
        total_files = len(file_paths)
        completed_files = 0
        
        while completed_files < total_files:
            try:
                progress = progress_queue.get(timeout=0.1)
                if progress_callback:
                    progress_callback(progress / total_files + completed_files / total_files)
            except Empty:
                pass
            
            # Check if any futures have completed
            for future in futures:
                if future.done():
                    future.result()  # This will raise any exceptions that occurred during processing
                    completed_files += 1
                    break

def run_crag_model(question: str) -> str:
    """Run the CRAG model with the given question."""
    crag_model = get_crag_model()
    return crag_model(question)
