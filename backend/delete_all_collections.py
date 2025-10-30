import chromadb
import grpc
from concurrent import futures

import collections_pb2
import collections_pb2_grpc

# -----------------------------
# Original code (unchanged)
# -----------------------------

client = chromadb.PersistentClient(path="./chroma_db")

def delete_all_collections():
    collections = [c.name for c in client.list_collections()]
    print("Before deletion:", collections)

    for col_name in collections:
        client.delete_collection(col_name)
        print(f"Deleted collection: {col_name}")

    print("After deletion:", [c.name for c in client.list_collections()])

def delete_collection(collection_name: str):
    if collection_name not in [c.name for c in client.list_collections()]:
        print(f"Collection {collection_name} does not exist.")
        return []
    client.delete_collection(collection_name)
    print(f"Deleted collection: {collection_name}")

    return [c.name for c in client.list_collections()]

# -----------------------------
# Minimal gRPC addition
# -----------------------------

class CollectionService(collections_pb2_grpc.CollectionServiceServicer):
    def DeleteCollection(self, request, context):
        collection_name = request.collection_name
        remaining = delete_collection(collection_name)
        return collections_pb2.DeleteCollectionResponse(
            remaining_collections=remaining
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    collections_pb2_grpc.add_CollectionServiceServicer_to_server(CollectionService(), server)
    server.add_insecure_port("[::]:50051")
    print("✅ gRPC server running on port 50051...")
    server.start()
    server.wait_for_termination()

# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    serve()
