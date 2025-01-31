import pypdf
from pymilvus import MilvusClient
from support_fun import make_emb
from tqdm import tqdm

reader = pypdf.PdfReader('Гражданский кодекс Российской Федерации ГК РФ части первая вторая третья и четве.pdf')
topics = []
final = ""
for i in tqdm(reader.pages):
    print(i.extract_text())
    final += i.extract_text()
for i in final.split("Статья")[1:]:
    topics.append("Статья" + i)
index = 0
data = []
for topic in tqdm(topics):
    data.append({"id": index, "ask_vector": make_emb("passage: " + topic), "ask_solve": topic})
    index += 1
client = MilvusClient(uri="http://localhost:19530")
res = client.insert(
    collection_name="cividoc",
    data=data)
