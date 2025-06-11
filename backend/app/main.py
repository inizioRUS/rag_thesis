import os
import uuid
from typing import Optional
from fastapi.staticfiles import StaticFiles
import yaml
from fastapi import FastAPI, Request, Form, Query, Cookie, Response
from fastapi import UploadFile, File, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
import requests
from starlette.responses import JSONResponse
from pydantic import BaseModel
from auth.hashing import verify_password, create_access_token, decode_token
from models.tg_bot import TelegramBot
from schemas.tg_bot import TelegramBotCreate
from services.tg_bot import create_new_tg_bot, launch_bot
from schemas.user import UserCreate
from schemas.index import IndexCreate
from services.user import get_current_user, create_user, get_all_users
from services.index import create_new_index, get_public_indices_page, get_user_indices, get_current_index, \
    get_tg_bot_by_index
from uuid import uuid4
from core.db import init_db
import yaml

running_bots = {}


def read_config():
    with open("config/config.yaml", "r") as file:
        config = yaml.safe_load(file)
    return config


config = read_config()
ml_address = config.get("ml", {}).get("address")
ml_port = config.get("ml", {}).get("port")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # URL вашего React-приложения
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Подключаем папку
app.mount("/static", StaticFiles(directory="C:/Users/garan/PycharmProjects/diplom/diplom/ml/app/extracted"), name="static")

templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup_event():
    await init_db()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    token = request.cookies.get("access_token")
    if token:
        user_id = decode_token(token)
        if user_id:
            user = await get_current_user(user_id)
        else:
            user = None
    else:
        user = None
    return templates.TemplateResponse("main.html", {"request": request, "user": user})


@app.get("/user")
async def user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Не авторизован")

    token = auth_header.split(" ")[1]
    print(token)
    user_id = decode_token(token)
    print(user_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Неверный токен")

    user = await get_current_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    print(user)
    return {"username": user.username}


# @app.get("/register", response_class=HTMLResponse)
# async def register_form(request: Request):
#     return templates.TemplateResponse("register.html", {"request": request})


class RegisterData(BaseModel):
    username: str
    password: str


@app.post("/register")
async def register(data: RegisterData):
    existing_users = await get_all_users()
    if any(u.username == data.username for u in existing_users):
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    user_id = uuid4()
    await create_user(UserCreate(id=user_id, username=data.username, password=data.password))
    token = create_access_token({"sub": str(user_id)})

    return {"message": "Успешный вход", "token": token}  # Возвращаем токен в теле ответа


# @app.get("/login", response_class=HTMLResponse)
# async def login_form(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request})

class LoginData(BaseModel):
    username: str
    password: str


@app.post("/login")
async def login(data: LoginData):
    users = await get_all_users()
    for user in users:
        if user.username == data.username and verify_password(data.password, user.hashed_password):
            token = create_access_token({"sub": str(user.id)})
            return {"message": "Успешный вход", "token": token}  # Возвращаем токен в теле ответа
    raise HTTPException(status_code=401, detail="Неверный логин или пароль")


@app.get("/main", response_class=HTMLResponse)
async def dashboard(request: Request):
    token = request.cookies.get("access_token")
    print(decode_token(token))
    user_id = uuid.UUID(decode_token(token))
    user = get_current_user(user_id)
    if not user:
        return RedirectResponse(url="/login")
    indices = await get_public_indices_page(page=1, per_page=12)
    print(indices)
    return templates.TemplateResponse("main.html", {"request": request, "user": user, "indices": indices})


@app.get("/logout")
async def logout():
    # Просто возвращаем сообщение, что выход выполнен
    return JSONResponse({"message": "Выход выполнен"})


@app.post("/upload/")
async def upload_and_forward(file: UploadFile = File(...)):
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Можно загружать только .zip архивы")

    try:
        files = {'file': (file.filename, await file.read(), file.content_type)}
        response = requests.post(f'http://{ml_address}:{ml_port}/upload', files=files)
        response.raise_for_status()
        return JSONResponse(content=response.json())

    except Exception as e:
        raise JSONResponse(content={"status": "ошибка"})


@app.get("/make_index", response_class=HTMLResponse)
async def render_make_index(request: Request):
    token = request.cookies.get("access_token")
    user = None
    if token:
        user_id = uuid.UUID(decode_token(token))
        user = await get_current_user(user_id)
    return templates.TemplateResponse("make_index.html", {"request": request, "user": user})


@app.post("/make_index")
async def create_index(
        request: Request,
        name: str = Form(...),
        description: str = Form(...),
        milvus_index_name: str = Form(...),
        is_private: bool = Form(False),
        file: UploadFile = File(...),
        type_llm: str | None = Form(...),
        token_llm: str | None = Form(...),
):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Не авторизован")

    token = auth_header.split(" ")[1]
    print(token)
    user_id = decode_token(token)
    print(user_id)
    user_id = uuid.UUID(decode_token(token))
    if type_llm == "local":
        data = {
            "id": uuid4(),
            "name": name,
            "description": description,
            "milvus_index_name": milvus_index_name,
            "is_private": bool(is_private),
            "user_id": user_id,
            "llm_type": "local",
            "token": None
        }
    else:
        data = {
            "id": uuid4(),
            "name": name,
            "description": description,
            "milvus_index_name": milvus_index_name,
            "is_private": bool(is_private),
            "user_id": user_id,
            "llm_type": "api",
            "token": token_llm
        }
    files = {'file': (file.filename, await file.read(), file.content_type)}
    response = requests.post(f'http://{ml_address}:{ml_port}/upload', files=files,
                             data={"index_name": milvus_index_name})
    await create_new_index(
        IndexCreate(**data))
    return JSONResponse({"task_id": response.json()["task_id"]})


@app.get("/api/indices")
async def get_indices(page: int = Query(1, ge=1), per_page: int = Query(12, ge=1, le=100)):
    indices = await get_public_indices_page(page=page, per_page=per_page)
    return JSONResponse(
        content={"indices": [{"id": str(i.id), "name": i.name, "description": i.description} for i in indices]}
    )


# @app.get("/user")
# async def user(request: Request,):
#     token = request.cookies.get("access_token")
#     print(token)
#     user = None
#     if token:
#         user_id = uuid.UUID(decode_token(token))
#         user = await get_current_user(user_id)
#     return JSONResponse(
#         content={"username": user.username}
#     )

# @app.get("/home", response_class=HTMLResponse)
# async def dashboard(request: Request):
#     token = request.cookies.get("access_token")
#     if not token:
#         return RedirectResponse(url="/login")
#
#     try:
#         user_id = uuid.UUID(decode_token(token))
#         user = get_current_user(user_id)
#     except Exception:
#         return RedirectResponse(url="/login")
#
#     if not user:
#         return RedirectResponse(url="/login")
#
#     indices = await get_user_indices(user_id)
#
#     return templates.TemplateResponse("home.html", {
#         "request": request,
#         "user": user,
#         "indices": indices
#     })


@app.get("/api/index/{id}", response_class=HTMLResponse)
async def read_index(request: Request, id: str):
    index_id = uuid.UUID(id)

    index = await get_current_index(index_id)

    if index is None:
        return HTMLResponse(content="Индекс не найден", status_code=404)

    return JSONResponse({"id": str(index.id), "name": index.name, "description": index.description})


class MessageRequest(BaseModel):
    message: str
    index_id: str


@app.post("/get_ml_response")
async def get_response(request: MessageRequest):
    # Получаем сообщение от клиента
    message = request.message
    index = await get_current_index(request.index_id)
    # Запрашиваем ответ у ML-сервиса
    response = requests.post(f'http://{ml_address}:{ml_port}/get_answer',
                             json={'message': message, "index_name": index.milvus_index_name, "llm_type": index.llm_type, "token": index.token})
    response_data = response.json()
    reply = response_data.get('reply', "Что-то пошло не так...")
    sources = response_data.get('sources', [])
    sources = list(map(lambda x: "http://localhost:8000/" + x, sources))
    print(sources)
    return JSONResponse(content={"reply": reply, "sources":sources})


class MessageRequestDoc(BaseModel):
    message: str
    index_id: str
    document_prompt:str

@app.post("/get_ml_document")
async def get_response(request: MessageRequestDoc):
    # Получаем сообщение от клиента
    message = request.message
    index = await get_current_index(request.index_id)
    # Запрашиваем ответ у ML-сервиса
    response = requests.post(f'http://{ml_address}:{ml_port}/get_document',
                             json={'message': message, "index_name": index.milvus_index_name, "llm_type": index.llm_type, "token": index.token, "document_prompt": request.document_prompt})
    response_data = response.json()
    reply = response_data.get('reply', "Что-то пошло не так...")
    sources = response_data.get('sources', [])
    download_link = response_data.get('download_link', "")
    download_link = "http://localhost:8000/" + download_link
    sources = list(map(lambda x: "http://localhost:8000/" + x, sources))
    print(sources)
    return JSONResponse(content={"reply": reply, "sources":sources, "download_link": download_link})

class BotConnectRequest(BaseModel):
    index_id: str
    bot_token: str


@app.get("/setting_index/{index_id}", response_class=HTMLResponse)
async def setting_index(request: Request, index_id: str):
    index_id = uuid.UUID(index_id)
    index = await get_current_index(index_id)
    telegram_bot = await get_tg_bot_by_index(index_id)
    if len(telegram_bot) != 0:
        telegram_bot = telegram_bot[0]
    if not index:
        return HTMLResponse("Индекс не найден", status_code=404)
    print(telegram_bot)
    return JSONResponse(
        content={"index": {"id": str(index.id), "name": index.name, "description": index.description,
                           "milvus_index_name": index.milvus_index_name, "is_private": index.is_private},
                 "telegram_bot": {"token": telegram_bot.token if telegram_bot else None,
                                  "bot_url": telegram_bot.bot_url if telegram_bot else None}}
    )


@app.post("/update_index_bot/{index_id}")
async def update_index_bot(index_id: uuid.UUID, bot_token: str = Form(...), bot_url: str = Form(...)):
    data = {
        'bot_url': bot_url,
        'token': bot_token,
        'search_index_id': index_id

    }

    await create_new_tg_bot(
        TelegramBotCreate(**data))
    index = await get_current_index(index_id)
    await launch_bot(index.milvus_index_name, bot_token, index.llm_type, index.token)
    return {"status": "okay"}
