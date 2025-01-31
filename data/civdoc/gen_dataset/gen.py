import json

data = []
with open("data.txt", "r", encoding="utf8") as text:
    index = 0
    qu = {}
    for i in text.read().split("\n"):
        if index % 2 == 0:
            qu["question"] = i
        else:
            qu["answer"] = i
            data.append(qu)
            qu = {}
        index += 1
with open("data.json", "w", encoding="utf8") as w:
    json.dump(data, w, ensure_ascii=False, indent=1)
