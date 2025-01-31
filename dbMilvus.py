from pymilvus import MilvusClient, Collection, connections


class DbMilvus:
    def __init__(self, ip, port):
        connections.connect(
            alias="default",
            host=ip,
            port=port
        )
        self.client = MilvusClient(uri=f"http://{ip}:{port}")

    def load(self, collection_name):
        collection = Collection(name=collection_name)
        collection.load()

    def insert(self, data, collection_name):
        self.client.insert(
            collection_name=collection_name,
            data=data)

    def search(self, config):
        res = self.client.search(
            **config
        )
        print(res)
        return res[0]