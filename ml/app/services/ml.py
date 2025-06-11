from .make_embedding import model, model_rerank
from core.db import search


def get_answer(index_name: str, query: str, llm) -> str:
    context, documents = give_documents(index_name, query)
    res = llm.invoke(query, context)
    return res, documents


def get_answer_doc(index_name: str, query: str, llm, document_prompt: str) -> str:
    context, documents = give_documents(index_name, query)
    res = llm.invoke_doc(query, context, document_prompt)
    return res, documents


def make_emb(text: str) -> list[float]:
    return model.encode(["passage: " + text])

def make_rereank(query: str, texts: list[str], k: int) -> list[float]:
    texts_gen = [
        query,
        *[i['entity']['text'] for i in texts]
    ]

    embeddings = model_rerank.encode(texts_gen, task="retrieval.passage")
    scores = embeddings[0] @ embeddings[1:].T
    print(len(scores))
    print(len(texts))
    texts = [x for _, x in sorted(zip(scores, texts), key=lambda x: -x[0])]
    return texts[:k]

def give_documents(index_name: str, query: str):
    config = {
        "collection_name": index_name,
        "data": [make_emb("query: " + query).tolist()[0]],
        "limit": 10,
        "search_params": {"metric_type": "COSINE", "params": {}},
        "output_fields": ["id", "text", "link", "all_text"]
    }
    res = search(
        config
    )
    res = [
        r for r in res if r["distance"] >= 0.78
    ]
    print([i["entity"]["link"] for i in res])
    res = make_rereank(query, res, 7)
    print([i["entity"]["link"] for i in res])
    context = ""
    document = []
    index = 1
    for i in res:
        if i["entity"]["link"] not in document:
            document.append(i["entity"]["link"])
            context += f"Документ {index}\n" + i["entity"]["all_text"] + "\n\n"
            index += 1
    return context, document
