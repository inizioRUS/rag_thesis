from sentence_transformers import SentenceTransformer
import torch
print(torch.cuda.is_available())
model = SentenceTransformer("intfloat/multilingual-e5-large", device='cuda')