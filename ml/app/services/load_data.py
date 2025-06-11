import os
import zipfile
from llama_index.core.node_parser import SentenceSplitter
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from llama_index.core.schema import Document, TextNode, Node
from core.db import load, insert
from services.make_embedding import model
from tqdm import tqdm
from bs4 import BeautifulSoup
from docx import Document as docxDoc
import fitz  # PyMuPDF
def load_data(file_path: str, task_id: str) -> list:
    extract_path = os.path.join("extracted", task_id)
    os.makedirs(extract_path, exist_ok=True)

    with zipfile.ZipFile(file_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)

    texts = []

    for root, _, files in os.walk(extract_path):
        for fname in files:
            fpath = os.path.join(root, fname)
            content = ""

            if fname.endswith(".txt"):
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().strip()

            elif fname.endswith(".html") or fname.endswith(".htm"):
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    soup = BeautifulSoup(f, "html.parser")
                    content = soup.get_text().strip()

            elif fname.endswith(".pdf"):
                try:
                    with fitz.open(fpath) as doc:
                        content = "\n".join([page.get_text() for page in doc]).strip()
                except Exception as e:
                    print(f"Ошибка при обработке PDF: {fpath} — {e}")

            elif fname.endswith(".docx"):
                try:
                    doc = docxDoc(fpath)
                    content = "\n".join([p.text for p in doc.paragraphs]).strip()
                except Exception as e:
                    print(f"Ошибка при обработке DOCX: {fpath} — {e}")

            if content:
                texts.append([content, fpath.replace('extracted', 'static')])

    return texts


def split_texts(texts_list: list) -> list:
    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=32)
    chunks = []
    nodes = []
    index = 0
    for text in texts_list:
        nodes.append(Document(text=text[0]))
        nodes[-1].metadata["link"] = text[1]
        nodes[-1].metadata["index"] = index
        index += 1
    nodes = splitter.get_nodes_from_documents(nodes)
    for node in nodes:
        node.metadata["window"] = texts_list[node.metadata["index"]][0]
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
        chunks_out.append({"embedding": embeddings[index], "text": chunks[index].text, "link": chunks[index].metadata["link"], "all_text": chunks[index].metadata["window"]})
    return chunks_out


def put_in_milvus(chunks: list, collection_name: str):
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
        FieldSchema(name="all_text", dtype=DataType.VARCHAR, max_length=65535),
        FieldSchema(name="link", dtype=DataType.VARCHAR, max_length=65535)
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
