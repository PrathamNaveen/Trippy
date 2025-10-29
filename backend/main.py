from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, Header
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os
from pdf_ingestion import ingest_pdf, query_vector_db, list_all_collections
from auth import create_session, get_session, get_all_session

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
# ✅ Session Dependency
# -------------------------------
def validate_session(session_id: str = Header(..., alias="session_id")):
    user = get_session(session_id)
    if user == 401:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if user is None:
        raise HTTPException(status_code=401, detail="Session Invalid or Expired")
    print("Authenticated user:", user)
    return user  # Injected into the endpoint

# -------------------------------
# ✅ Routes
# -------------------------------

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/create_session")
async def create_user_session(username: str = Form(...), password: str = Form(...)):
    try:
        session_id = create_session(username, password)
        return {"session_id": session_id}
    except Exception as e:
        return {"error": str(e)}


@app.get("/session/{session_id}")
async def get_user_session(session_id: str):
    try:
        response = get_session(session_id)
        if response == 401:
            return {"error": "Unauthorized"}
        return {"session_data": response}
    except Exception as e:
        return {"error": str(e)}


@app.get("/list_collections")
async def list_collections(user: str = Depends(validate_session)):
    """Get all collections stored in Chroma DB."""
    try:
        collections = list_all_collections()
        return {"collections": collections}
    except Exception as e:
        return {"error": str(e)}


@app.post("/upload_pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    collection_name: str = Form(None),  # read collection_name from FormData
    user: str = Depends(validate_session)  # session validated
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
async def query_itinerary(
    request: QueryRequest,
    user: str = Depends(validate_session)  # session validated
):
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
    uvicorn.run(app, host="0.0.0.0", port=port)
