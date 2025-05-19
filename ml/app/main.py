from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Request
from fastapi.responses import JSONResponse
from llama_index.llms.ollama import Ollama
from pydantic import BaseModel
from uuid import uuid4
from typing import Dict
import shutil
import os
import threading

from llm.llm import LLMAggregate
from core.db import load
from services.ml import get_answer
from fastapi.middleware.cors import CORSMiddleware

from services.load_data import load_data, split_texts, vectorize, put_in_milvus

app = FastAPI()
llm = LLMAggregate(Ollama(model="llama3.1:8b-instruct-q4_0", temperature=0.1, request_timeout=1000, additional_kwargs={"num_predict": 200}))
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # или ['http://localhost:3000'] конкретно
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TASKS: Dict[str, str] = {}  # task_id -> status
UPLOAD_DIR = "uploads"


class QueryRequest(BaseModel):
    index_name: str
    query: str


@app.post("/upload")
async def upload_zip(index_name: str = Form(...), file: UploadFile = File(...)):
    task_id = str(uuid4())
    TASKS[task_id] = "not_started"

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, f"{task_id}.zip")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    thread = threading.Thread(target=process_zip_task, args=(index_name, task_id, file_path))
    thread.start()

    return {"task_id": task_id}


@app.get("/status/{task_id}")
async def check_status(task_id: str):
    status = TASKS.get(task_id)
    if not status:
        return {"status": "Не начато"}
    return {"status": status}


class Message(BaseModel):
    message: str
    index_name: str


@app.post("/get_answer", response_class=JSONResponse)
async def chat(request: Request, msg: Message):
    message = msg.message
    index_name = msg.index_name

    response = get_answer(index_name, message, llm)

    return JSONResponse(content={"reply": response})


# @app.post("/query")
# async def ask_query(request: QueryRequest):
#     index = INDICES.get(request.index_name)
#     if not index:
#         raise HTTPException(status_code=404, detail="Индекс не найден")
#
#     # Векторизация и поиск — можно заменить на Milvus + sentence-transformers
#     embedding = fake_vectorize(request.query)
#     results = fake_search(index, embedding)
#
#     return {"results": results}


def process_zip_task(index_name: str, task_id: str, file_path: str):
    try:
        TASKS[task_id] = "in_progress"
        print(1)
        texts = load_data(file_path, task_id)
        print(2)
        chunks = split_texts(texts)
        print(3)
        chunks = vectorize(chunks)
        print(4)
        put_in_milvus(chunks, index_name)
        print(5)
        TASKS[task_id] = "готово"
    except Exception as e:
        TASKS[task_id] = "error"
        print(f"Ошибка при обработке: {e}")

# def fake_search(index, vector):
#     return [{"text": t, "score": 0.99} for t in index]

# -------------------------------------------------------------
