import os
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from backend.document_processing import pdf_processor, jsonl_processor
from backend.database import mongodb_client
from backend.ai_models import model_loader
from backend.utils import text_splitter, metadata_extractor

def process_file(file_path: str, file_name: str) -> Generator[Dict[str, Any], None, None]:
    """Process a single file and yield its metadata and content."""
    file_type = os.path.splitext(file_name)[1].lower()
    
    if file_type == '.pdf':
        content, metadata = pdf_processor.process_pdf(file_path)
        yield {'content': content, 'metadata': metadata}
    elif file_type in ['.jsonl', '.json']:
        for content, metadata in jsonl_processor.process_jsonl(file_path):
            # Add file-specific metadata
            metadata['file_name'] = file_name
            metadata['file_type'] = file_type
            
            # Extract additional metadata if needed
            additional_metadata = metadata_extractor.extract_metadata(content)
            metadata.update(additional_metadata)
            
            yield {'content': content, 'metadata': metadata}
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

def create_embeddings(texts: List[str], progress_callback=None) -> List[List[float]]:
    """Create embeddings for a list of texts."""
    model = model_loader.load_embedding_model()
    embeddings = []
    total = len(texts)
    
    for i, text in enumerate(texts):
        embedding = model.get_embedding(text)
        embeddings.append(embedding)
        if progress_callback:
            progress_callback(i + 1, total)
    
    return embeddings

def batch_process_file(file_path: str, file_name: str, progress_callback=None) -> None:
    """Process a file in batches, create embeddings, and store in the database."""
    processed_data_generator = process_file(file_path, file_name)
    
    chunk_index = 0
    for processed_data in processed_data_generator:
        content = processed_data['content']
        metadata = processed_data['metadata']
        
        chunks = text_splitter.split_text(content)
        
        def embedding_progress(current, total):
            if progress_callback:
                progress_callback(current / total)
        
        embeddings = create_embeddings(chunks, embedding_progress)
        
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

def process_files(file_paths: List[str], file_names: List[str], progress_callback=None) -> None:
    """Process multiple files concurrently."""
    with ThreadPoolExecutor() as executor:
        futures = []
        for file_path, file_name in zip(file_paths, file_names):
            future = executor.submit(batch_process_file, file_path, file_name, progress_callback)
            futures.append(future)
        
        for future in as_completed(futures):
            future.result()  # This will raise any exceptions that occurred during processing
