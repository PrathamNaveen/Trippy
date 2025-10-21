from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os
from pdf_ingestion import ingest_pdf, query_vector_db

# Load env
load_dotenv()

# FastAPI app
app = FastAPI(title="Italy Trip RAG Backend")

port = int(os.getenv("PORT", 8000))

# CORS
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

# Routes
@app.get("/")
async def root():
    return {"message": "Italy Trip Backend is running!"}

@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        num_chunks = ingest_pdf(file.file)
        return {"message": f"PDF ingested successfully with {num_chunks} chunks!"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/query")
async def query_itinerary(request: QueryRequest):
    question = request.question
    try:
        # 1️⃣ Retrieve relevant chunk(s)
        relevant_chunks = query_vector_db(question, top_k=3)
        relevant_chunk = relevant_chunks[0] if relevant_chunks else ""

        # 2️⃣ Send prompt to Groq LLM
        prompt = f"Use the following itinerary info to answer the question:\n\n{relevant_chunk}\n\nQuestion: {question}\nAnswer:"
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant"
        )
        ai_answer = response.choices[0].message.content
        print(f"✅ Generated answer from Groq LLM.: {ai_answer}")

        return {
            "question_received": question,
            "answer": ai_answer,
            "relevant_chunk": relevant_chunk
        }
    except Exception as e:
        return {"question_received": question, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=port)