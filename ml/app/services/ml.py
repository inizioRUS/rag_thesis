from .make_embedding import model
from core.db import search


def get_answer(index_name: str, query: str, llm) -> str:
    context = give_documents(index_name, query)
    res = llm.invoke(query, context)
    return res


def make_emb(text: str) -> list[float]:
    return model.encode(["passage: " + text])


def give_documents(index_name: str, query: str):
    config = {
        "collection_name": index_name,
        "data": [make_emb("query: " + query).tolist()[0]],
        "limit": 10,
        "search_params": {"metric_type": "COSINE", "params": {}},
        "output_fields": ["id", "text"]
    }
    res = search(
        config
    )
    context = ""
    for i in res:
        context += i["entity"]["text"] + "\n\n"
    return context
