import chromadb

client = chromadb.PersistentClient(path="./chroma_db")

# List all collections
collections = [c.name for c in client.list_collections()]
print("Before deletion:", collections)

# # Delete each collection
# for col_name in collections:
#     client.delete_collection(col_name)
#     print(f"Deleted collection: {col_name}")

# Verify
print("After deletion:", [c.name for c in client.list_collections()])
