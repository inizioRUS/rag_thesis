from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from transformers import LlamaTokenizerFast
from sentence_transformers import SentenceTransformer
import docx

embed_model = SentenceTransformer(model_name_or_path="intfloat/multilingual-e5-large", device="cuda")
tokenizer = LlamaTokenizerFast.from_pretrained("hf-internal-testing/llama-tokenizer")


def make_emb(text: str) -> list[float]:
    return embed_model.encode(["passage: " + text])


def token_count(text: str) -> int:
    return len(tokenizer.encode(text))


def getText(filename):
    doc = docx.Document(filename)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return '\n'.join(fullText)
