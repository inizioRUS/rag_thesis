from pymilvus import CollectionSchema, FieldSchema, DataType, MilvusClient

client = MilvusClient(uri="http://localhost:19530")

if client.has_collection(collection_name="cividoc"):
    client.drop_collection(collection_name="cividoc")

id_ask = FieldSchema(
    name="id",
    dtype=DataType.INT64,
    is_primary=True,
)

ask_intro = FieldSchema(
    name="ask_vector",
    dtype=DataType.FLOAT_VECTOR,
    dim=1024,
)
ask_solve = FieldSchema(
    name="ask_solve",
    dtype=DataType.VARCHAR,
    max_length=65535,
)
schema = CollectionSchema(
    fields=[id_ask, ask_intro, ask_solve],
    description="AsK cividoc"
)
collection_name = "cividoc"

client.create_collection(collection_name=collection_name, schema=schema)

index_params = MilvusClient.prepare_index_params()

index_params.add_index(
    field_name="ask_vector",
    metric_type="COSINE",
    index_type="IVF_FLAT",
    index_name="vector_index",
    params={"nlist": 1024}
)

client.create_index(
    collection_name="cividoc",
    index_params=index_params,
    sync=False
)
