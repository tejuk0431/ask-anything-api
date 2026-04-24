from fastapi import FastAPI
from openai import OpenAI
import os

app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/")
def home():
    return {"message": "Ask Anything API is running"}


@app.get("/ask")
def ask(q: str):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": q}
            ]
        )
        answer = response.choices[0].message.content
        return {"question": q, "answer": answer}
    
    except Exception as e:
        return {"error": str(e)}