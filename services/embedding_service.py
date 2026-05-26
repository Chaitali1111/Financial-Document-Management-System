import chromadb

client = chromadb.Client()

collection = client.create_collection(
    name="documents"
)


def generate_embedding(text):

    return [float(len(text))] * 10


def store_embeddings(chunks):

    for i, chunk in enumerate(chunks):

        embedding = generate_embedding(chunk)

        collection.add(
            documents=[chunk],
            embeddings=[embedding],
            ids=[str(i)]
        )

    return "Embeddings stored successfully"


def search_query(query):

    query_embedding = generate_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=2
    )

    return results