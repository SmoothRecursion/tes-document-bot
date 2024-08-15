import json
from typing import Generator, Dict, Any, Tuple

def process_jsonl(file_path: str) -> Generator[Tuple[str, Dict[str, Any]], None, None]:
    """
    Process a JSONL file and yield its content and metadata line by line.
    
    Args:
    file_path (str): Path to the JSONL file.
    
    Yields:
    Tuple[str, Dict[str, Any]]: A tuple containing the content as a string and metadata as a dictionary for each line.
    """
    metadata = {}
    
    with open(file_path, 'r') as file:
        for line in file:
            json_obj = json.loads(line)
            content = json_obj.get('text', '').strip()
            
            # Extract metadata from the first line (assuming metadata is consistent across the file)
            if not metadata:
                metadata = {k: v for k, v in json_obj.items() if k != 'text'}
            
            yield content, metadata

def format_for_similarity(content: str, metadata: Dict[str, Any]) -> str:
    """
    Format the JSONL data into a string suitable for semantic similarity.
    
    Args:
    content (str): The main content of the JSONL entry.
    metadata (Dict[str, Any]): The metadata associated with the content.
    
    Returns:
    str: A formatted string representation of the data.
    """
    formatted = [f"Content: {content}"]
    for key, value in metadata.items():
        formatted.append(f"{key}: {value}")
    return " | ".join(formatted)

def process_jsonl_for_similarity(file_path: str) -> Generator[str, None, None]:
    """
    Process a JSONL file and yield formatted strings for semantic similarity.
    
    Args:
    file_path (str): Path to the JSONL file.
    
    Yields:
    str: A formatted string representation of each entry, suitable for semantic similarity.
    """
    for content, metadata in process_jsonl(file_path):
        yield format_for_similarity(content, metadata)
