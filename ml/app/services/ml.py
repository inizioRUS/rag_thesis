import uuid

from tqdm import tqdm

from .load_data import put_in_milvus
from .make_embedding import model, model_rerank
from core.db import search

from core.db import insert, load


def get_answer(index_name: str, working_context, msg_index_name, queries: list[str], llm) -> str:
    context, documents = give_documents(index_name, queries[-1])
    old_msg = give_old_msg(msg_index_name, queries[-1])
    queries_text = "\n".join([("user: " if i % 2 == 0 else "bot: ") + queries[i]for i in range(len(queries))])
    print(queries_text)
    new_working_context = llm.invoke_update_working_context(old_msg, working_context, queries_text)
    res = llm.invoke(queries[-1], context, new_working_context, old_msg, queries_text)
    save_milvus(msg_index_name, [queries[-1], res])
    return res, documents, new_working_context


def get_answer_doc(index_name: str, working_context, msg_index_name, queries: list[str], llm,
                   document_prompt: str) -> str:
    print(queries)
    context, documents = give_documents(index_name, queries[-1])
    old_msg = give_old_msg(msg_index_name, queries[-1])
    queries_text = "\n".join([("user: " if i % 2 == 0 else "bot: ") + queries[i]for i in range(len(queries))])
    print(queries_text)
    new_working_context = llm.invoke_update_working_context(old_msg, context, working_context, queries_text)
    res = llm.invoke_doc(queries[-1], context, new_working_context, old_msg, queries, document_prompt)
    save_milvus(msg_index_name, [queries[-1], res])
    return res, documents, new_working_context


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
        "output_fields": ["id", "text", "all_text", "link"]
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


def give_old_msg(index_name: str, query: str):
    config = {
        "collection_name": index_name,
        "data": [make_emb("query: " + query).tolist()[0]],
        "limit": 5,
        "search_params": {"metric_type": "COSINE", "params": {}},
        "output_fields": ["id", "text"]
    }

    res = search(
        config
    )
    res = [
        r for r in res if r["distance"] >= 0.78
    ]
    res = make_rereank(query, res, 7)
    context = ""
    index = 1
    for i in res:
        context += f"Сообщение {index}:\n" + i["entity"]["text"] + "\n\n"
        index += 1
    return context


def save_milvus(msg_index_name: str, queries):
    embeddings = model.encode(
        [f"passage: {text}" for text in queries],
        show_progress_bar=True,
        convert_to_numpy=True
    )
    embeddings = embeddings.tolist()
    chunks_out = []
    for index in tqdm(range(len(queries))):
        chunks_out.append(
            {"embedding": embeddings[index], "text": queries[index]})
    load(msg_index_name)
    insert(chunks_out, msg_index_name)
