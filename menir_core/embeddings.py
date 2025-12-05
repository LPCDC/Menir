# menir_core/embeddings.py

from __future__ import annotations
import abc
import hashlib
from typing import List


class EmbeddingBackend(abc.ABC):
    """Interface para qualquer backend de embedding."""

    dim: int

    @abc.abstractmethod
    def embed(self, text: str) -> List[float]:
        """Gera um vetor para o texto fornecido."""
        raise NotImplementedError


class DummyHashEmbedding(EmbeddingBackend):
    """Backend determinístico simples, baseado em hash – só para testes."""

    def __init__(self, dim: int = 32) -> None:
        self.dim = dim

    def embed(self, text: str) -> List[float]:
        # Usa SHA256 como base, repete bytes até preencher dim
        h = hashlib.sha256(text.encode("utf-8")).digest()
        vals = list(h)
        out = []
        for i in range(self.dim):
            out.append(vals[i % len(vals)] / 255.0)
        return out


# Backend padrão atual – pode ser trocado depois por OpenAI/Groq/Gemini
_default_backend: EmbeddingBackend | None = None


def get_default_backend() -> EmbeddingBackend:
    global _default_backend
    if _default_backend is None:
        _default_backend = DummyHashEmbedding(dim=32)
    return _default_backend


def embed_text(text: str) -> List[float]:
    """Função utilitária usada pelo resto do Menir."""
    backend = get_default_backend()
    return backend.embed(text)
