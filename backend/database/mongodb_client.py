import os
from pymongo import MongoClient
from dotenv import load_dotenv
from langchain.vectorstores import MongoDBAtlasVectorSearch
from backend.ai_models.model_loader import load_embedding_model

# Load environment variables
load_dotenv()

class AtlasClient:
    def __init__(self, atlas_uri=None, dbname="automotive_docs", embedding_model="openai"):
        if atlas_uri is None:
            atlas_uri = os.getenv("MONGODB_URI")
        if not atlas_uri:
            raise ValueError("MONGODB_URI environment variable is not set")
        self.mongodb_client = MongoClient(atlas_uri)
        self.database = self.mongodb_client[dbname]
        self.vector_store = None

    def ping(self):
        """A quick way to test if we can connect to Atlas instance"""
        return self.mongodb_client.admin.command('ping')

    def get_collection(self, collection_name):
        """Get a collection by name"""
        return self.database[collection_name]

    def find(self, collection_name, filter={}, limit=0):
        """Find documents in a collection"""
        collection = self.get_collection(collection_name)
        return list(collection.find(filter=filter, limit=limit))

    def insert_document(self, collection_name, document):
        """Insert a single document into the collection."""
        collection = self.get_collection(collection_name)
        return collection.insert_one(document)

    def get_document_by_id(self, collection_name, document_id):
        """Retrieve a single document by its ID."""
        collection = self.get_collection(collection_name)
        return collection.find_one({"_id": document_id})

    def update_document(self, collection_name, document_id, update_data):
        """Update a document by its ID."""
        collection = self.get_collection(collection_name)
        return collection.update_one({"_id": document_id}, {"$set": update_data})

    def delete_document(self, collection_name, document_id):
        """Delete a document by its ID."""
        collection = self.get_collection(collection_name)
        return collection.delete_one({"_id": document_id})

    def search_documents(self, collection_name, query, limit=10):
        """Search for documents based on a text query."""
        collection = self.get_collection(collection_name)
        return list(collection.find({"$text": {"$search": query}}).limit(limit))

    def initialize_vector_store(self, collection_name="documents", index_name="default"):
        """Initialize the vector store for similarity search."""
        embeddings = load_embedding_model(self.embedding_model)
        self.vector_store = MongoDBAtlasVectorSearch(
            collection=self.get_collection(collection_name),
            embedding=embeddings,
            index_name=index_name
        )

    def similarity_search(self, query, k=5):
        """Perform a similarity search using the vector store."""
        if self.vector_store is None:
            raise ValueError("Vector store is not initialized. Call initialize_vector_store() first.")
        return self.vector_store.similarity_search(query, k=k)

# Usage example:
if __name__ == "__main__":
    client = AtlasClient()
    try:
        client.ping()
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
