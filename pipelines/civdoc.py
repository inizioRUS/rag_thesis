from dbMilvus import DbMilvus
from support_fun import make_emb


class CiviDocService:
    def __init__(self, llm, db: DbMilvus):
        self.llm = llm
        self.db = db
        self.db.load("cividoc")

    def ask(self, text: str):
        config = {
            "collection_name": "cividoc",
            "data": [make_emb("query: " + text).tolist()[0]],
            "limit": 10,
            "search_params": {"metric_type": "COSINE", "params": {}},
            "output_fields": ["id", "ask_solve"]
        }
        res = self.db.search(
            config
        )
        context = ""
        for i in res:
            context += i["entity"]["ask_solve"] + "\n\n"

        res = self.llm.invoke(text, context)
        return res
