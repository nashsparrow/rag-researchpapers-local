import json
import os

from config import MODEL_NAME, NORMALIZE_EMBEDDINGS

os.environ.setdefault("USE_TF", "0")

from sentence_transformers import SentenceTransformer


def create_embeddings(input_text):
    # Load the model.
    model = SentenceTransformer(MODEL_NAME)

    embeddings = model.encode(input_text, normalize_embeddings=NORMALIZE_EMBEDDINGS)
    return embeddings
