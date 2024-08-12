import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MongoDB Atlas connection string from environment variable
MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI environment variable is not set")

# Create a new client and connect to the server
client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))

# Select the database and collection
db = client.get_database("automotive_docs")
collection = db.get_collection("documents")

def insert_document(document):
    """Insert a single document into the collection."""
    return collection.insert_one(document)

def get_all_documents():
    """Retrieve all documents from the collection."""
    return list(collection.find())

def get_document_by_id(document_id):
    """Retrieve a single document by its ID."""
    return collection.find_one({"_id": document_id})

def update_document(document_id, update_data):
    """Update a document by its ID."""
    return collection.update_one({"_id": document_id}, {"$set": update_data})

def delete_document(document_id):
    """Delete a document by its ID."""
    return collection.delete_one({"_id": document_id})

def search_documents(query, limit=10):
    """Search for documents based on a text query."""
    return list(collection.find({"$text": {"$search": query}}).limit(limit))

# Test the connection
try:
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
