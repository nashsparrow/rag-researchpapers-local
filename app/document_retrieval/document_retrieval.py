import json
import os

import faiss
from config import MODEL_NAME

os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")


def load_model():
    # Load model
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(MODEL_NAME)

    # Load Faiss index
    index = faiss.read_index("data/processed/document_embeddings.index")

    # Load chunks
    with open("data/processed/chunked_data.json", "r") as f:
        chunks = json.load(f)

    print(f"Model {MODEL_NAME} loaded successfully.")
    print("FAISS index loaded successfully.")
    print(f"{len(chunks)} chunks loaded successfully.")

    return model, index, chunks


def retrieve_relevant_chunks(query, model, index, chunks, top_k=5):
    # Create embedding for query
    query_embedding = model.encode([query], normalize_embeddings=True)

    # Search the index for relevant chunks
    distances, indices = index.search(query_embedding, top_k)

    cleaned_indices = clean_and_sort_indices(distances, indices)

    # Retrieve the corresponding chunks and attach scores
    relevant_chunks = []
    for idx, score in cleaned_indices.items():
        chunk = chunks[idx].copy() if isinstance(chunks[idx], dict) else chunks[idx]
        if isinstance(chunk, dict):
            chunk["score"] = float(score)
        relevant_chunks.append(chunk)

    return relevant_chunks


def clean_and_sort_indices(distances, indices):

    dict_with_distances = {}

    for i, idx in enumerate(indices[0]):
        if idx not in dict_with_distances:
            dict_with_distances[idx] = distances[0][i]

    sorted_dict = dict(
        sorted(dict_with_distances.items(), key=lambda item: item[1], reverse=True)
    )

    return sorted_dict
