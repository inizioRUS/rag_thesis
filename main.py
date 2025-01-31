from fastapi import FastAPI
from pydantic import BaseModel
from llama_index.llms.ollama import Ollama
from fastapi.middleware.cors import CORSMiddleware
from askservice import AskService
from dbMilvus import DbMilvus
from llm.llm_aggregate import LLMAggregate
from pipelines.civdoc import CiviDocService
from db import db_session


class QueryBody(BaseModel):
    service: str
    text: str


class QueryBody_sib(BaseModel):
    text: str


client = DbMilvus("localhost", 19530)
llm2 = LLMAggregate(Ollama(model="llama3.1:latest", temperature=0.1, request_timeout=1000, context_window=5000,additional_kwargs={"num_predict": 200}))
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
sevises = {"civi": CiviDocService(llm2, client)}
askservice = AskService(sevises)
db_session.global_init("db/data.sqlite")


@app.post("/query")
async def query(queryBody: QueryBody):
    return askservice.ask(queryBody.service, queryBody.text)
