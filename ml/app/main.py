from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Request
from fastapi.responses import JSONResponse
from llama_index.llms.ollama import Ollama
from pydantic import BaseModel
from uuid import uuid4
from typing import Dict
import shutil
import os
import threading
import markdown
import pdfkit
from llm.llm import LLMAggregate
from core.db import load
from llm.llm_api import LLMAAPI
from services.ml import get_answer, get_answer_doc
from fastapi.middleware.cors import CORSMiddleware

from services.load_data import load_data, split_texts, vectorize, put_in_milvus

app = FastAPI()
llm = LLMAggregate(Ollama(model="llama3.1:8b-instruct-q4_0", temperature=0.1, request_timeout=1000,
                          additional_kwargs={"num_predict": 200}))
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
    llm_type: str
    token: str | None


@app.post("/get_answer", response_class=JSONResponse)
async def chat(request: Request, msg: Message):
    message = msg.message
    index_name = msg.index_name
    llm_type = msg.llm_type
    token = msg.token

    if llm_type == "api":
        llm_api = LLMAAPI(token)
        response, documents = get_answer(index_name, message, llm_api)
    else:
        response, documents = get_answer(index_name, message, llm)
    return JSONResponse(content={"reply": response, "sources": documents})

class MessageDoc(BaseModel):
    message: str
    index_name: str
    llm_type: str
    token: str | None
    document_prompt:str

@app.post("/get_document", response_class=JSONResponse)
async def chat(request: Request, msg: MessageDoc):
    message = msg.message
    index_name = msg.index_name
    llm_type = msg.llm_type
    token = msg.token
    document_prompt = msg.document_prompt
    if llm_type == "api":
        llm_api = LLMAAPI(token)
        response, documents = get_answer_doc(index_name, message, llm_api, document_prompt)
    else:
        response, documents = get_answer_doc(index_name, message, llm, document_prompt)
    html_text = markdown.markdown(response, extensions=["fenced_code"])
    task_id = str(uuid4())

    # Оборачивание в HTML-документ
    html_full = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: sans-serif; line-height: 1.6; padding: 2em; }}
            h1, h2, h3 {{ color: #333; }}
            pre, code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 4px; }}
        </style>
    </head>
    <body>
    {html_text}
    </body>
    </html>
    """
    pdfkit.from_string(html_full, f"C:/Users/garan/PycharmProjects/diplom/diplom/ml/app/extracted/pdf_output/{task_id}.pdf", configuration=pdfkit.configuration(wkhtmltopdf="C:\Program Files\wkhtmltopdf\\bin\wkhtmltopdf.exe"))
    return JSONResponse(content={"reply": response, "sources": documents, "download_link":f"static\\pdf_output\\{task_id}.pdf"})


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
