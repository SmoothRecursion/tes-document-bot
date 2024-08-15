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
