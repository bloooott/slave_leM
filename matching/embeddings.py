from sentence_transformers import SentenceTransformer
import numpy as np

_model = None

def get_model():
    global _model
    if _model is None:
        # Modèle léger, gratuit, tourne en local (pas d'API)
        _model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    return _model

def embed_text(text: str) -> np.ndarray:
    model = get_model()
    return model.encode(text, normalize_embeddings=True)

def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    return float(np.dot(vec_a, vec_b))