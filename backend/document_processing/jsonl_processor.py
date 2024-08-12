import json
from typing import Tuple, Dict, Any

def process_jsonl(file_path: str) -> Tuple[str, Dict[str, Any]]:
    """
    Process a JSONL file and extract its content and metadata.
    
    Args:
    file_path (str): Path to the JSONL file.
    
    Returns:
    Tuple[str, Dict[str, Any]]: A tuple containing the content as a string and metadata as a dictionary.
    """
    content = ""
    metadata = {}
    
    with open(file_path, 'r') as file:
        for line in file:
            json_obj = json.loads(line)
            if 'text' in json_obj:
                content += json_obj['text'] + "\n"
            
            # Extract metadata from the first line (assuming metadata is consistent across the file)
            if not metadata:
                metadata = {k: v for k, v in json_obj.items() if k != 'text'}
    
    return content.strip(), metadata
