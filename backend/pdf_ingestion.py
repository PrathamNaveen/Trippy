from PyPDF2 import PdfReader
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
import chromadb

# Embeddings model
embeddings_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": False}
)

# 2️⃣ Initialize / connect to Chroma DB
client = chromadb.PersistentClient(path="./chroma_db")
collection_name = "italy__trip_itinerary"

# Create or get collection
try:
    collection = client.get_collection(collection_name)
except Exception:
    collection = client.create_collection(collection_name)


def ingest_pdf(pdf_path_or_file) -> int:
    """
    Ingests a PDF: extracts text, splits into chunks, converts to embeddings,
    and stores them in Chroma DB.
    Returns the number of chunks ingested.
    """
    # 1️⃣ Read PDF
    if isinstance(pdf_path_or_file, str):
        reader = PdfReader(pdf_path_or_file)
    else:
        reader = PdfReader(pdf_path_or_file)

    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    if not text.strip():
        raise ValueError("No text could be extracted from the PDF!")

    # 2️⃣ Split into chunks (use CharacterTextSplitter)
    splitter = CharacterTextSplitter.from_tiktoken_encoder(
        separator="\n",
        encoding_name="cl100k_base",
        chunk_size=300,
        chunk_overlap=20
    )
    chunks = splitter.split_text(text)

    # 3️⃣ Embed + store each chunk
    for i, chunk in enumerate(chunks):
        vector = embeddings_model.embed_query(chunk)
        collection.add(ids=[f"chunk_{i}"], documents=[chunk], embeddings=[vector])

    print(f"✅ PDF ingested successfully with {len(chunks)} chunks!")
    return len(chunks)


def query_vector_db(query_text: str, top_k: int = 1):
    """
    Queries the Chroma vector DB and returns the most relevant chunk(s).
    """
    query_vector = embeddings_model.embed_query(query_text)
    results = collection.query(query_embeddings=[query_vector], n_results=top_k)

    print(f"✅ Retrieved {len(results['documents'][0])} relevant chunk(s) from vector DB.")
    
    if not results or "documents" not in results or not results["documents"]:
        return []

    return results["documents"][0]

if __name__ == "__main__":
    # Example usage
    pdf_path = "./itineraries/italy_trip_itinerary.pdf"
    ingest_pdf(pdf_path)
    query = "What are the top attractions in Rome?"
    relevant_chunks = query_vector_db(query, top_k=2)
    print("Relevant Chunks:", relevant_chunks)
