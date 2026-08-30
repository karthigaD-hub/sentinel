import numpy as np


class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self._model = None

    def _load_model(self) -> None:
        if self._model is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        except ImportError as exc:
            raise RuntimeError(
                "sentence-transformers is not installed. Install with: pip install sentence-transformers"
            ) from exc

    def embed(self, texts: str | list[str]) -> np.ndarray:
        self._load_model()
        if isinstance(texts, str):
            texts = [texts]
        embeddings = self._model.encode(texts, convert_to_numpy=True)
        return embeddings

    def embed_query(self, query: str) -> np.ndarray:
        return self.embed([query])[0]

    @property
    def available(self) -> bool:
        try:
            from sentence_transformers import SentenceTransformer  # noqa: F401
            return True
        except ImportError:
            return False


embedding_service = EmbeddingService()
