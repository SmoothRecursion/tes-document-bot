from typing import List

def split_text(text: str, max_chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Split the input text into chunks of approximately max_chunk_size characters,
    with a specified overlap between chunks.
    """
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0

    for word in words:
        if current_size + len(word) + 1 > max_chunk_size and current_chunk:
            chunks.append(' '.join(current_chunk))
            overlap_words = current_chunk[-overlap:]
            current_chunk = overlap_words
            current_size = sum(len(w) + 1 for w in overlap_words)
        
        current_chunk.append(word)
        current_size += len(word) + 1

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks
