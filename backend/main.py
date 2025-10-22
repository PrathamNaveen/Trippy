from fastapi import FastAPI, UploadFile, File, Query, Form
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os
from pdf_ingestion import ingest_pdf, query_vector_db, list_all_collections

# Load environment
load_dotenv()

app = FastAPI(title="Multi-Collection RAG Backend")
port = int(os.getenv("PORT", 8000))

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Groq setup
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("Please set the GROQ_API_KEY environment variable!")
groq_client = Groq(api_key=groq_api_key)


# Request model
class QueryRequest(BaseModel):
    question: str
    collection_name: str


# -------------------------------
# ✅ Routes
# -------------------------------

@app.get("/")
async def root():
    return {"message": "Multi-RAG Backend is running!"}


@app.get("/list_collections")
async def list_collections():
    """Get all collections stored in Chroma DB."""
    try:
        collections = list_all_collections()
        return {"collections": collections}
    except Exception as e:
        return {"error": str(e)}


@app.post("/upload_pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    collection_name: str = Form(None)  # read collection_name from FormData
):
    try:
        # If collection_name not provided, use file name (without extension)
        collection = collection_name or file.filename.rsplit(".", 1)[0]

        print("Collection Name: ", collection)

        # Ingest PDF into the specified collection
        num_chunks = ingest_pdf(file.file, collection_name=collection)

        return {"message": f"✅ PDF ingested into '{collection}' with {num_chunks} chunks!"}
    except Exception as e:
        return {"error": str(e)}


@app.post("/query")
async def query_itinerary(request: QueryRequest):
    """Query a specific collection."""
    try:
        relevant_chunks = query_vector_db(request.question, collection_name=request.collection_name, top_k=3)
        prompt = f"Use the following info to answer the question:\n\n{relevant_chunks}\n\nQuestion: {request.question}\nAnswer:"
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant"
        )
        ai_answer = response.choices[0].message.content
        return {"question_received": request.question, "answer": ai_answer}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=port)
