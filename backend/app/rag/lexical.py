import math
import re
from collections import Counter, defaultdict

import numpy as np

TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:[._-][a-z0-9]+)*")
STOPWORDS = frozenset(
    {"a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how", "in", "is", "it", "of", "on", "or", "that", "the", "this", "to", "what", "which", "with"}
)


def tokenize(text: str) -> list[str]:
    return [token for token in TOKEN_PATTERN.findall(text.lower()) if token not in STOPWORDS]


class BM25Index:
    def __init__(self, documents: list[list[str]], k1: float = 1.5, b: float = 0.75) -> None:
        self._k1 = k1
        self._b = b
        self._doc_lengths = np.array([len(doc) for doc in documents], dtype=np.float32)
        self._avg_length = float(self._doc_lengths.mean()) if len(documents) else 0.0
        self._postings: dict[str, list[tuple[int, int]]] = defaultdict(list)
        for index, doc in enumerate(documents):
            for term, frequency in Counter(doc).items():
                self._postings[term].append((index, frequency))
        self._size = len(documents)

    def scores(self, query_tokens: list[str]) -> np.ndarray:
        scores = np.zeros(self._size, dtype=np.float32)
        if self._size == 0:
            return scores
        for term in set(query_tokens):
            postings = self._postings.get(term)
            if not postings:
                continue
            document_frequency = len(postings)
            idf = math.log(1 + (self._size - document_frequency + 0.5) / (document_frequency + 0.5))
            for doc_index, frequency in postings:
                length_norm = 1 - self._b + self._b * self._doc_lengths[doc_index] / max(self._avg_length, 1e-9)
                scores[doc_index] += idf * frequency * (self._k1 + 1) / (frequency + self._k1 * length_norm)
        return scores
