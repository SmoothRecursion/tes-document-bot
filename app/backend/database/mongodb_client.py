import os
from pymongo import MongoClient
from dotenv import load_dotenv
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings

# Load environment variables
load_dotenv()

class AtlasClient:
    def __init__(self, atlas_uri=None, dbname="automotive_docs", collection_name="documents", index_name="vector_index"):
        if atlas_uri is None:
            atlas_uri = os.getenv("MONGODB_URI")
        if not atlas_uri:
            raise ValueError("MONGODB_URI environment variable is not set")
        self.mongodb_client = MongoClient(atlas_uri)
        self.database = self.mongodb_client[dbname]
        self.embeddings = OpenAIEmbeddings()
        self._initialize_vector_store(collection_name, index_name)

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

    def _initialize_vector_store(self, collection_name="documents", index_name="vector_index"):
        """Initialize the vector store for similarity search."""
        self.vector_store = MongoDBAtlasVectorSearch(
            collection=self.get_collection(collection_name),
            embedding=self.embeddings,
            index_name=index_name,
        )

    def insert_document_with_embedding(self, document):
        """Insert a document into the collection and create an embedding for it."""
        self.vector_store.add_documents([document])

    def insert_documents_with_embeddings(self, documents):
        """Insert multiple documents into the collection and create embeddings for them."""
        self.vector_store.add_documents(documents)

    def similarity_search(self, query, k=5):
        """Perform a similarity search using the vector store."""
        return self.vector_store.similarity_search(query, k=k)

    def list_collections(self):
        """List all available collections in the database."""
        return self.database.list_collection_names()

# Usage example:
if __name__ == "__main__":
    client = AtlasClient()
    try:
        client.ping()
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
