import asyncio
import importlib.util

import numpy as np

from app.core.config import settings


class EmbeddingService:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self._model = None

    @property
    def loaded(self) -> bool:
        return self._model is not None

    @staticmethod
    def library_installed() -> bool:
        return importlib.util.find_spec("sentence_transformers") is not None

    def load(self) -> None:
        if self._model is not None:
            return
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(self.model_name)

    def _encode(self, texts: list[str]) -> np.ndarray:
        self.load()
        vectors = self._model.encode(texts, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False)
        return np.asarray(vectors, dtype=np.float32)

    async def embed(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, 0), dtype=np.float32)
        return await asyncio.to_thread(self._encode, texts)


embedding_service = EmbeddingService(settings.rag_embedding_model)
