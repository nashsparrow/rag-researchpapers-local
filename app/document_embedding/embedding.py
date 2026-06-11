import json
import os
import faiss
import numpy as np
from config import MODEL_NAME, NORMALIZE_EMBEDDINGS


os.environ.setdefault("USE_TF", "0")

from sentence_transformers import SentenceTransformer

# Load the model once at module import to avoid reloading on every call.
_model = SentenceTransformer(MODEL_NAME)


def create_embeddings(input_text):
    # Accept a single string or a list of strings and return a 2D numpy array
    if isinstance(input_text, str):
        texts = [input_text]
    else:
        texts = list(input_text)

    embeddings = _model.encode(texts, normalize_embeddings=NORMALIZE_EMBEDDINGS)
    embeddings = np.asarray(embeddings)

    # Ensure embeddings are 2D: (n, d). For a single input this will be (1, d).
    if embeddings.ndim == 1:
        embeddings = np.expand_dims(embeddings, 0)

    return embeddings


def get_embedding_dimension():
    return _model.get_sentence_embedding_dimension()

def get_index():
    dimension = get_embedding_dimension()
    index = faiss.IndexFlatIP(dimension)
    return index

def save_index(index, file_path):
    faiss.write_index(index, file_path)