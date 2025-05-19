import os
import zipfile
from llama_index.core.node_parser import SentenceSplitter
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from llama_index.core.schema import Document, TextNode, Node
from core.db import load, insert
from services.make_embedding import model
from tqdm import tqdm

def load_data(file_path: str, task_id: str) -> list:
    extract_path = os.path.join("extracted", task_id)
    os.makedirs(extract_path, exist_ok=True)

    with zipfile.ZipFile(file_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)

    texts = []
    for root, _, files in os.walk(extract_path):
        for fname in files:
            if fname.endswith(".txt"):
                fpath = os.path.join(root, fname)
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().strip()
                    if content:
                        texts.append(content)
    return texts


def split_texts(texts_list: list) -> list:
    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=64)
    chunks = []
    documents = [Document(text=text) for text in texts_list]
    nodes = splitter.get_nodes_from_documents(documents)
    for node in nodes:
        print(node)
        chunks.append(node)
    return chunks


def vectorize(chunks: list) -> list:
    embeddings = model.encode(
        [f"passage: {text}" for text in chunks],
        show_progress_bar=True,
        convert_to_numpy=True
    )
    embeddings = embeddings.tolist()
    chunks_out = []
    for index in tqdm(range(len(chunks))):
        chunks_out.append({"embedding": embeddings[index], "text": chunks[index].text})
    return chunks_out


def put_in_milvus(chunks: list, collection_name: str):
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535)
    ]
    schema = CollectionSchema(fields, description="Text search index")
    collection = Collection(name=collection_name, schema=schema)

    # Вставка данных
    insert(chunks, collection_name)

    # Создание индекса
    collection.create_index(field_name="embedding", index_params={
        "metric_type": "COSINE",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 1024}
    })

    load(collection_name)
