import os
from typing import List, Dict, Any, Generator
from concurrent.futures import ThreadPoolExecutor, as_completed
from backend.document_processing import jsonl_processor
from backend.database import mongodb_client
from backend.ai_models.model_loader import load_embedding_model, get_crag_model
from backend.utils.text_splitter import split_text
from backend.utils.metadata_extractor import extract_metadata

def process_file(file_path: str, file_name: str) -> Generator[Dict[str, Any], None, None]:
    """Process a single file and yield its metadata and content."""
    file_type = os.path.splitext(file_name)[1].lower()
    
    if file_type in ['.jsonl', '.json']:
        for content, metadata in jsonl_processor.process_jsonl(file_path):
            # Add file-specific metadata
            metadata['file_name'] = file_name
            metadata['file_type'] = file_type
            
            # Extract additional metadata
            additional_metadata = extract_metadata(content)
            metadata.update(additional_metadata)
            
            yield {'content': content, 'metadata': metadata}
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

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

def batch_process_file(file_path: str, file_name: str, embedding_model: str = "openai", progress_callback=None) -> None:
    """Process a file in batches, create embeddings, and store in the database."""
    processed_data_generator = process_file(file_path, file_name)
    
    chunk_index = 0
    for processed_data in processed_data_generator:
        content = processed_data['content']
        metadata = processed_data['metadata']
        
        chunks = split_text(content, chunk_size=1000, chunk_overlap=100)
        
        def embedding_progress(current, total):
            if progress_callback:
                progress_callback(current / total)
        
        embeddings = create_embeddings(chunks, embedding_model, embedding_progress)
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            document = {
                'content': chunk,
                'embedding': embedding,
                'metadata': metadata,
                'chunk_index': chunk_index + i,
            }
            mongodb_client.insert_document(document)
            if progress_callback:
                progress_callback((i + 1) / len(chunks))
        
        chunk_index += len(chunks)

def process_files(file_paths: List[str], file_names: List[str], embedding_model: str = "openai", progress_callback=None) -> None:
    """Process multiple files concurrently."""
    with ThreadPoolExecutor() as executor:
        futures = []
        for file_path, file_name in zip(file_paths, file_names):
            future = executor.submit(batch_process_file, file_path, file_name, embedding_model, progress_callback)
            futures.append(future)
        
        for future in as_completed(futures):
            future.result()  # This will raise any exceptions that occurred during processing

def run_crag_model(question: str) -> str:
    """Run the CRAG model with the given question."""
    crag_model = get_crag_model()
    return crag_model(question)
