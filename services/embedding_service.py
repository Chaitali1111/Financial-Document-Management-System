from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

dimension = 384

index = faiss.IndexFlatL2(dimension)

stored_chunks = []


def store_embeddings(chunks):

    global stored_chunks

    stored_chunks = chunks

    embeddings = []

    for chunk in chunks:

        embedding = model.encode(chunk)

        embeddings.append(embedding)

    embeddings = np.array(embeddings).astype("float32")

    index.add(embeddings)

    return "Embeddings stored in FAISS successfully"


def search_query(query):

    query_embedding = model.encode([query]).astype("float32")

    distances, indices = index.search(query_embedding, k=1)

    best_match = stored_chunks[indices[0][0]]

    return best_match