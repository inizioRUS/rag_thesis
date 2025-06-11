from sentence_transformers import SentenceTransformer
import torch

print(torch.cuda.is_available())
model = SentenceTransformer("intfloat/multilingual-e5-large")

model_rerank = SentenceTransformer("jinaai/jina-embeddings-v3", trust_remote_code=True)

print(torch.cuda.is_available())
