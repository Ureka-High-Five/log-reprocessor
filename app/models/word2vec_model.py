from gensim.models import KeyedVectors


class Word2VecModel:
    _model = None

    @classmethod
    def load_model(cls, model_path: str):
        if cls._model is None:
            print("모델 로딩 중...")
            cls._model = KeyedVectors.load_word2vec_format(model_path, binary=True)
            print("모델 로드 완료!")
        return cls._model

    @classmethod
    def get_vector(cls, word: str):
        if cls._model is None:
            raise RuntimeError("모델이 아직 로드되지 않았습니다.")
        return cls._model.get_vector(word)

    @classmethod
    def similarity(cls, word1: str, word2: str) -> float:
        if cls._model is None:
            raise RuntimeError("모델이 아직 로드되지 않았습니다.")
        return cls._model.similarity(word1, word2)
