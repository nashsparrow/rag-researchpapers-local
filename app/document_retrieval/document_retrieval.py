import json

import faiss
from sentence_transformers import SentenceTransformer

from config import MODEL_NAME


def load_model():
    # Load model
    model = SentenceTransformer(MODEL_NAME) 

    # Load Faiss index
    index = faiss.read_index("data/processed/document_embeddings.index")

    # Load chunks
    with open("data/processed/chunked_data.json", "r") as f:
        chunks = json.load(f)

    print(f"Model {MODEL_NAME} loaded successfully.")
    print(f"FAISS index loaded successfully.")
    print(f"{len(chunks)} chunks loaded successfully.")

    return model, index, chunks

def retrieve_relevant_chunks(query, model, index, chunks, top_k=5):
    # Create embedding for query
    query_embedding = model.encode([query], normalize_embeddings=True)

    # Search the index for relevant chunks
    distances, indices = index.search(query_embedding, top_k)

    # Retrieve the corresponding chunks
    relevant_chunks = [chunks[i] for i in indices[0]]

    return relevant_chunks
