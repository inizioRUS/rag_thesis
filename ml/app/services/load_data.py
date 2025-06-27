import os
import zipfile

import requests
from llama_index.core.node_parser import SentenceSplitter
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from llama_index.core.schema import Document, TextNode, Node, MetadataMode
from core.db import load, insert
from services.make_embedding import model
from tqdm import tqdm
from bs4 import BeautifulSoup
from docx import Document as docxDoc
import fitz  # PyMuPDF
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright, Playwright


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


def is_valid_url(url, base_domain):
    parsed = urlparse(url)
    return parsed.scheme.startswith("https") and base_domain in url


def extract_text(html):
    soup = BeautifulSoup(html, "html.parser")
    print(soup)
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)


def parsing_web(link: str, task_id: str):
    visited_urls = set()
    return _parsing_web(link, task_id, visited_urls, base_domain=link)


def _parsing_web(link: str, task_id: str, visited_urls, depth=1, max_depth=40, base_domain=None):
    if depth > max_depth or link in visited_urls:
        return []
    visited_urls.add(link)
    parsed_url = urlparse(link)
    if base_domain is None:
        base_domain = parsed_url.netloc
    if not is_valid_url(link, base_domain):
        return []

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page()
            page.goto(link)
            browser.close()
    except Exception as e:
        print(f"Error fetching {link}: {e}")
        return []

    html = page.content()
    text = extract_text(html)
    # Результат: пара (текст, источник)
    results = [(text, link)]

    soup = BeautifulSoup(html, "html.parser")
    for link_tag in soup.find_all("a", href=True):
        next_url = urljoin(link, link_tag['href'])
        results.extend(_parsing_web(next_url, task_id, visited_urls, depth + 1, max_depth, base_domain))
        print(next_url)

    return results


def split_texts(texts_list: list, chunk_size, overlap) -> list:
    splitter = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
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
        chunks_out.append(
            {"embedding": embeddings[index], "text": chunks[index].text, "link": chunks[index].metadata["link"],
             "all_text": chunks[index].metadata["window"]})
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


def make_index_chat(collection_name: str):
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
    ]
    schema = CollectionSchema(fields, description="Text search index")
    collection = Collection(name=collection_name, schema=schema)

    insert([], collection_name)

    # Создание индекса
    collection.create_index(field_name="embedding", index_params={
        "metric_type": "COSINE",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 1024}
    })

    load(collection_name)
