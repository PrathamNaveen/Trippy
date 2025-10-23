import chromadb

client = chromadb.PersistentClient(path="./chroma_db")

# List all collections
collections = [c.name for c in client.list_collections()]
print("Collections: ", collections)
