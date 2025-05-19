from pymilvus import MilvusClient, Collection, connections

connections.connect(
    alias="default",
    host="localhost",
    port=19530
)
client = MilvusClient(uri=f"http://localhost:19530")


def load(collection_name):
    collection = Collection(name=collection_name)
    collection.load()


def insert(data, collection_name):
    client.insert(
        collection_name=collection_name,
        data=data)


def search(config):
    res = client.search(
        **config
    )
    return res[0]
