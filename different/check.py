import json
from sklearn.metrics.pairwise import cosine_similarity

from different.solves.cleargpt import ClearGPT
from different.solves.multiraggpt import RagGPT
from solves.clearllama import ClearLlamma
from tqdm import tqdm
from support_fun import make_emb

avg_cos_sim = 0
count = 0

model = RagGPT()

with open("C:\\Users\garan\PycharmProjects\sovetnik_for_doc\data\civdoc\gen_dataset\data.json", "r",
          encoding="utf8") as w:
    data = json.load(w)
for i in tqdm(data):
    q = i["question"]
    a = i["answer"]
    answer_model = model.run(q)
    avg_cos_sim += cosine_similarity(make_emb(a).reshape(1, -1), make_emb(answer_model).reshape(1, -1))[0][0]
    count += 1
    print(avg_cos_sim / count)

print(avg_cos_sim / count)
