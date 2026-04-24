# RAG Document Chatbot API

A FastAPI-based AI application that allows users to upload PDF documents and ask questions based on the document content using Retrieval-Augmented Generation (RAG).

## Features

- PDF upload and text extraction
- Document chunking
- OpenAI embeddings
- FAISS vector search
- AI-powered question answering
- Source citations with page references
- Streamlit user interface
- Swagger API documentation
- Deployed on Render

## Tech Stack

- Python
- FastAPI
- OpenAI API
- FAISS
- PyPDF
- NumPy
- Streamlit
- Render

## Architecture

1. User uploads a PDF document.
2. Text is extracted using PyPDF.
3. Text is split into smaller chunks.
4. Each chunk is converted into embeddings using OpenAI.
5. Embeddings are stored in a FAISS vector index.
6. User submits a question.
7. Question is converted into an embedding.
8. FAISS retrieves the most relevant chunks.
9. LLM generates an answer using retrieved context.
10. API returns the answer with source citations.

## API Endpoints

### Home

**GET /**

Returns API status.

```json
{
  "message": "RAG Document Chatbot API is running"
}


POST /upload

Uploads a PDF, extracts readable text, creates chunks, generates embeddings, and stores them in FAISS.

Example response:

{
  "filename": "sample.pdf",
  "chunks_created": 25,
  "message": "PDF uploaded and indexed successfully"
}


## Ask Question

**GET /ask-doc?q=your_question**

Retrieves relevant document chunks and generates an answer from the uploaded PDF.

### Example Response

```json
{
  "question": "What is this document about?",
  "answer": "The document explains...",
  "sources": [
    {
      "filename": "sample.pdf",
      "page": 2,
      "preview": "This section explains..."
    }
  ]
}

Run Locally
Install dependencies
python -m pip install -r requirements.txt
Set OpenAI API Key (Windows PowerShell)
$env:OPENAI_API_KEY="your_api_key_here"
Run FastAPI backend
python -m uvicorn main:app --reload
Run Streamlit UI
python -m streamlit run app.py
Live Demo
Backend API

https://ask-anything-api.onrender.com

Swagger Docs

https://ask-anything-api.onrender.com/docs

Screenshots
UI Interface






## Screenshots
!### UI Interface
![UI](screenshot1.png) 

### Answer with Sources
![Answer](screenshot2.png)