import csv
from typing import Generator, Dict, Any, List

def process_csv(file_path: str) -> Generator[Dict[str, Any], None, None]:
    """
    Process a CSV file and yield its content as structured data.
    
    Args:
    file_path (str): Path to the CSV file.
    
    Yields:
    Dict[str, Any]: A dictionary containing the structured data for each row.
    """
    with open(file_path, 'r', newline='', encoding='utf-8-sig') as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader)
        
        for row in csv_reader:
            data = {}
            for i, value in enumerate(row):
                if value.strip():  # Only include non-empty values
                    data[headers[i]] = value.strip()
            
            if data:  # Only yield non-empty rows
                yield data

def format_for_similarity(data: Dict[str, Any]) -> str:
    """
    Format the structured data into a string suitable for semantic similarity.
    
    Args:
    data (Dict[str, Any]): The structured data for a single row.
    
    Returns:
    str: A formatted string representation of the data.
    """
    formatted = []
    for key, value in data.items():
        formatted.append(f"{key}: {value}")
    return " | ".join(formatted)

def process_csv_for_similarity(file_path: str) -> Generator[str, None, None]:
    """
    Process a CSV file and yield formatted strings for semantic similarity.
    
    Args:
    file_path (str): Path to the CSV file.
    
    Yields:
    str: A formatted string representation of each row, suitable for semantic similarity.
    """
    for data in process_csv(file_path):
        yield format_for_similarity(data)
