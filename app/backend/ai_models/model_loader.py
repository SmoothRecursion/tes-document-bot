from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from .langgraph_crag import run_crag

def load_embedding_model(model_name="openai"):
    """
    Load and return the specified embedding model.
    
    Args:
        model_name (str): The name of the embedding model to load. 
                          Options: "openai" or "huggingface"
    
    Returns:
        An instance of the specified embedding model.
    """
    if model_name.lower() == "openai":
        return OpenAIEmbeddings()
    elif model_name.lower() == "huggingface":
        return HuggingFaceEmbeddings()
    else:
        raise ValueError(f"Unsupported model: {model_name}")

def get_crag_model():
    """
    Return the function to run the CRAG model.
    
    Returns:
        The run_crag function from the langgraph_crag module.
    """
    return run_crag
