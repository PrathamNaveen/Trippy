from PyPDF2 import PdfReader
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
import chromadb

# Initialize embedding model
embeddings_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": False}
)

# Initialize / connect to Chroma DB
client = chromadb.PersistentClient(path="./chroma_db")


# -------------------------------
# ✅ Collection management utils
# -------------------------------

def list_all_collections():
    """Return a list of all collection names in Chroma DB."""
    collections = client.list_collections()
    return [c.name for c in collections]


def get_collection(collection_name: str):
    """Return an existing collection if found, else raise an error."""
    existing = list_all_collections()
    if collection_name not in existing:
        raise ValueError(f"Collection '{collection_name}' does not exist.")
    return client.get_collection(collection_name)


def create_collection(collection_name: str):
    """Create a new Chroma collection."""
    try:
        return client.create_collection(collection_name)
    except Exception as e:
        raise RuntimeError(f"Failed to create collection '{collection_name}': {e}")


# -------------------------------
# ✅ Core PDF and Query logic
# -------------------------------

def ingest_pdf(pdf_path_or_file, collection_name: str) -> int:
    """
    Ingest a PDF: extract text, split into chunks, embed, and store in Chroma DB.
    If collection does not exist, create it.
    """
    # Ensure collection exists
    existing_collections = list_all_collections()
    if collection_name in existing_collections:
        collection = get_collection(collection_name)
    else:
        collection = create_collection(collection_name)

    # Read PDF
    reader = PdfReader(pdf_path_or_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    if not text.strip():
        raise ValueError("No text could be extracted from the PDF!")

    # Split into chunks
    splitter = CharacterTextSplitter.from_tiktoken_encoder(
        separator="\n",
        encoding_name="cl100k_base",
        chunk_size=300,
        chunk_overlap=20
    )
    chunks = splitter.split_text(text)

    # Embed + store each chunk
    for i, chunk in enumerate(chunks):
        vector = embeddings_model.embed_query(chunk)
        collection.add(ids=[f"{collection_name}_chunk_{i}"], documents=[chunk], embeddings=[vector])

    print(f"✅ PDF ingested into '{collection_name}' with {len(chunks)} chunks!")
    return len(chunks)


def query_vector_db(query_text: str, collection_name: str, top_k: int = 3):
    """Queries an existing Chroma collection for relevant chunks."""
    collection = get_collection(collection_name)
    query_vector = embeddings_model.embed_query(query_text)
    results = collection.query(query_embeddings=[query_vector], n_results=top_k)

    if not results or "documents" not in results or not results["documents"]:
        print(f"⚠️ No relevant chunks found in '{collection_name}'.")
        return []

    print(f"✅ Retrieved {len(results['documents'][0])} chunks from '{collection_name}' collection.")
    return results["documents"][0]
