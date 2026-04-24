from fastapi import FastAPI, UploadFile, File, HTTPException
from openai import OpenAI
from pypdf import PdfReader
import os
import numpy as np
import faiss

app = FastAPI()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

chunks = []
index = None
uploaded_filename = None


@app.get("/")
def home():
    return {"message": "RAG Document Chatbot API is running"}


def extract_text_from_pdf(file):
    reader = PdfReader(file)
    pages_text = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()
        if page_text:
            pages_text.append({
                "page": page_number,
                "text": page_text
            })

    return pages_text


def split_text_by_page(pages_text, chunk_size=500):
    result = []

    for page in pages_text:
        words = page["text"].split()

        for i in range(0, len(words), chunk_size):
            chunk_text = " ".join(words[i:i + chunk_size])
            result.append({
                "page": page["page"],
                "text": chunk_text
            })

    return result


def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global chunks, index, uploaded_filename

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        pages_text = extract_text_from_pdf(file.file)

        if not pages_text:
            raise HTTPException(
                status_code=400,
                detail="No readable text found in the PDF"
            )

        chunks = split_text_by_page(pages_text)

        embeddings = []
        for chunk in chunks:
            embeddings.append(get_embedding(chunk["text"]))

        embedding_array = np.array(embeddings).astype("float32")

        index = faiss.IndexFlatL2(len(embedding_array[0]))
        index.add(embedding_array)

        uploaded_filename = file.filename

        return {
            "filename": uploaded_filename,
            "chunks_created": len(chunks),
            "message": "PDF uploaded and indexed successfully"
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ask-doc")
def ask_document(q: str):
    global chunks, index, uploaded_filename

    if index is None:
        raise HTTPException(
            status_code=400,
            detail="No document uploaded yet. Please upload a PDF first."
        )

    try:
        question_embedding = np.array([get_embedding(q)]).astype("float32")

        distances, indexes = index.search(question_embedding, k=3)

        retrieved_chunks = []
        for i in indexes[0]:
            retrieved_chunks.append(chunks[i])

        context = "\n\n".join(
            [
                f"Source page {chunk['page']}:\n{chunk['text']}"
                for chunk in retrieved_chunks
            ]
        )

        prompt = f"""
        Answer the question using only the document context below.
        If the answer is not available in the context, say:
        "I could not find the answer in the uploaded document."

        Document context:
        {context}

        Question:
        {q}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a document question-answering assistant. Use only the provided context."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        sources = []
        for chunk in retrieved_chunks:
            sources.append({
                "filename": uploaded_filename,
                "page": chunk["page"],
                "preview": chunk["text"][:250]
            })

        return {
            "question": q,
            "answer": response.choices[0].message.content,
            "sources": sources
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))