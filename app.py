from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

app = FastAPI()

model = SentenceTransformer("all-MiniLM-L6-v2")

class TextRequest(BaseModel):
    text: str

@app.post("/embed")
def create_embedding(req: TextRequest):
    vector = model.encode(req.text).tolist()
    return {"embedding": vector}