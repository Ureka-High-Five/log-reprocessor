from app.models.db_w2v_mapper import translate_genre
import numpy as np
from app.models.word2vec_model import Word2VecModel


def calc_user_vector(user_weights):
    weighted_vectors = []
    for name, weight in user_weights.items():
        try:
            name = translate_genre(name)
            vector = Word2VecModel.get_vector(name)
            weighted_vectors.append(vector * weight)
        except KeyError:
            print(f"[WARN] '{name}' 벡터 없음, 스킵")
            continue

    if not weighted_vectors:
        return []

    avg_vector = np.mean(weighted_vectors, axis=0)

    return avg_vector


def get_vector(keyword):
    return Word2VecModel.get_vector(keyword)


def calc_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)

    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)
