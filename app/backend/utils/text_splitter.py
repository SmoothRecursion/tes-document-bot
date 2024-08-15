from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter

def split_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 100) -> List[str]:
    """
    Split the input text into chunks using LangChain's RecursiveCharacterTextSplitter.
    
    :param text: The input text to be split.
    :param chunk_size: The maximum size of each chunk.
    :param chunk_overlap: The overlap between chunks.
    :return: A list of text chunks.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    return text_splitter.split_text(text)
