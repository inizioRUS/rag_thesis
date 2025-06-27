from sentence_transformers import SentenceTransformer
import torch
from transformers import AutoModel

print(torch.cuda.is_available())
model = SentenceTransformer("intfloat/multilingual-e5-large", device='cuda')


model_rerank =  SentenceTransformer("jinaai/jina-embeddings-v3", trust_remote_code=True, device='cuda')

print(torch.cuda.is_available())