import os
import logging
from typing import List, Dict, Any, Generator
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue, Empty
from langchain_core.documents import Document
from backend.document_processing import jsonl_processor, csv_processor
from backend.database.mongodb_client import AtlasClient
from backend.ai_models.model_loader import load_embedding_model, get_crag_model
from backend.utils.text_splitter import split_text
from backend.utils.metadata_extractor import extract_metadata

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

def batch_process_file(file_path: str, file_name: str, progress_callback=None, atlas_client: AtlasClient = None) -> int:
    if atlas_client is None:
        atlas_client = AtlasClient()
    """Process a file in batches and store in the database. Returns the total number of chunks processed."""
    logger.info(f"Starting to process file: {file_name}")
    processed_data_generator = process_file(file_path, file_name)
    
    chunk_index = 0
    total_chunks = 0
    documents = []

    for processed_data in processed_data_generator:
        content = processed_data['content']
        metadata = processed_data['metadata']
        
        chunks = split_text(content, chunk_size=1000, chunk_overlap=100)
        total_chunks += len(chunks)
        
        for i, chunk in enumerate(chunks):
            document = Document(
                page_content=chunk,
                metadata={
                    **metadata,
                    'chunk_index': chunk_index + i,
                }
            )
            documents.append(document)
        
        chunk_index += len(chunks)
    
    logger.info(f"Processed {total_chunks} chunks for file: {file_name}")
    
    # Insert documents in batches
    batch_size = 100
    total_inserted = 0
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        atlas_client.insert_documents_with_embeddings(batch)
        total_inserted += len(batch)
        logger.debug(f"Inserted batch of {len(batch)} documents. Total inserted: {total_inserted}")
        if progress_callback:
            progress_callback(len(batch))
    
    logger.info(f"Finished processing file: {file_name}. Total chunks: {total_chunks}, Total inserted: {total_inserted}")
    return total_chunks

def process_files(file_paths: List[str], file_names: List[str], progress_callback=None, atlas_client: AtlasClient = None) -> None:
    if atlas_client is None:
        atlas_client = AtlasClient()
    """Process multiple files concurrently."""
    logger.info(f"Starting to process {len(file_paths)} files")
    progress_queue = Queue()
    total_chunks = 0
    processed_chunks = 0
    
    def queue_progress_callback(chunks_processed):
        progress_queue.put(chunks_processed)
    
    with ThreadPoolExecutor() as executor:
        # First, get the total number of chunks
        logger.info("Calculating total number of chunks")
        chunk_counts = list(executor.map(batch_process_file, file_paths, file_names, [None]*len(file_paths), [atlas_client]*len(file_paths)))
        total_chunks = sum(chunk_counts)
        logger.info(f"Total chunks to process: {total_chunks}")
        
        # Now process the files
        futures = []
        for file_path, file_name in zip(file_paths, file_names):
            future = executor.submit(batch_process_file, file_path, file_name, queue_progress_callback, atlas_client)
            futures.append(future)
        
        while processed_chunks < total_chunks:
            try:
                chunks = progress_queue.get(timeout=0.1)
                processed_chunks += chunks
                logger.debug(f"Processed {chunks} chunks. Total: {processed_chunks}/{total_chunks}")
                if progress_callback:
                    progress_callback(processed_chunks / total_chunks)
            except Empty:
                pass
            
            # Check if any futures have completed
            for future in futures:
                if future.done():
                    try:
                        future.result()  # This will raise any exceptions that occurred during processing
                    except Exception as e:
                        logger.error(f"Error processing file: {str(e)}")
                        logger.exception(e)
    
    logger.info(f"Finished processing all files. Total chunks processed: {processed_chunks}")

def run_crag_model(question: str) -> str:
    """Run the CRAG model with the given question."""
    crag_model = get_crag_model()
    return crag_model(question)
