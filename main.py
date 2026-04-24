from fastapi import FastAPI, UploadFile, File
from openai import OpenAI
from pypdf import PdfReader
import os
import numpy as np
import faiss

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

chunks = []
index = None


@app.get("/")
def home():
    return {"message": "RAG Document Chatbot API is running"}


def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


def split_text(text, chunk_size=500):
    words = text.split()
    result = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        result.append(chunk)

    return result


def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global chunks, index

    text = extract_text_from_pdf(file.file)
    chunks = split_text(text)

    embeddings = []

    for chunk in chunks:
        embedding = get_embedding(chunk)
        embeddings.append(embedding)

    embedding_array = np.array(embeddings).astype("float32")

    index = faiss.IndexFlatL2(len(embedding_array[0]))
    index.add(embedding_array)

    return {
        "filename": file.filename,
        "chunks_created": len(chunks),
        "message": "PDF uploaded and indexed successfully"
    }


@app.get("/ask-doc")
def ask_document(q: str):
    global chunks, index

    if index is None:
        return {"error": "No document uploaded yet"}

    question_embedding = np.array([get_embedding(q)]).astype("float32")

    distances, indexes = index.search(question_embedding, k=3)

    context = "\n\n".join([chunks[i] for i in indexes[0]])

    prompt = f"""
    Answer the question using only the context below.

    Context:
    {context}

    Question:
    {q}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You answer questions based only on the provided document context."},
            {"role": "user", "content": prompt}
        ]
    )

    return {
        "question": q,
        "answer": response.choices[0].message.content
    }