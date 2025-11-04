"""Semantic embedding generation using sentence transformers."""

import asyncio
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """
    Semantic embedding generation service.

    Uses sentence transformers for generating dense vector representations
    of text for semantic similarity search.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str = "cpu") -> None:
        self._model_name = model_name
        self._device = device
        self._model: SentenceTransformer = None  # type: ignore

    async def _load_model(self) -> None:
        """Lazy load the embedding model."""
        if self._model is None:
            loop = asyncio.get_event_loop()
            self._model = await loop.run_in_executor(
                None, SentenceTransformer, self._model_name
            )
            self._model.to(self._device)

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text."""
        await self._load_model()

        # Run embedding generation in thread pool
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            None, lambda: self._model.encode(text, convert_to_numpy=True)
        )

        return embedding.tolist()

    async def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts (more efficient)."""
        await self._load_model()

        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None, lambda: self._model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        )

        return embeddings.tolist()

    async def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute cosine similarity between two embeddings."""
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        # Cosine similarity
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return float(similarity)
