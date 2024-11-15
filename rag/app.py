from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import numpy as np
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer
from typing import List

app = FastAPI()

embedding_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

db_user = 'postgres'
db_password = 'CS230password'
db_host = 'database-1.cdi4gywsaigf.us-east-2.rds.amazonaws.com'
db_port = 5432
db_name = 'postgres'

db_connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

class QueryRequest(BaseModel):
    query: str
    k: int

class Document(BaseModel):
    id: int
    text: str
    source: str

def get_documents(query: str, k: int = 5) -> List[Document]:
    embedding = np.array(embedding_model.encode(query))

    with psycopg2.connect(db_connection_string) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM document ORDER BY embedding <-> %s LIMIT %s", (embedding, k))
            rows = cur.fetchall()
            documents = [
                Document(id=row[0], text=row[1], source=row[2]) for row in rows
            ]
            return documents

@app.post("/query", response_model=List[Document])
async def query_documents(query_request: QueryRequest):
    try:
        documents = get_documents(query_request.query, query_request.k)
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
