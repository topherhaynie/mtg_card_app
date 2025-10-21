"""Caching utilities for deck suggestions and combo searches.

Provides LRU caching for expensive operations like RAG searches and combo detection.
"""

import hashlib
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class SuggestionCache:
    """Cache for deck suggestion results."""

    def __init__(self, max_size: int = 128):
        """Initialize cache with maximum size.

        Args:
            max_size: Maximum number of cached entries (default: 128)

        """
        self.max_size = max_size
        self._rag_cache = {}
        self._combo_cache = {}
        self._hits = 0
        self._misses = 0

    @staticmethod
    def _hash_dict(d: dict) -> str:
        """Create a stable hash from a dictionary."""
        # Sort keys for consistent hashing
        json_str = json.dumps(d, sort_keys=True)
        return hashlib.md5(json_str.encode()).hexdigest()

    @staticmethod
    def _deck_hash(deck) -> str:
        """Create a hash from deck cards and commander."""
        cards_sorted = tuple(sorted(deck.cards))
        commander = deck.commander or ""
        data = {"cards": cards_sorted, "commander": commander}
        return SuggestionCache._hash_dict(data)

    def get_rag_results(self, query: str, n_results: int):
        """Get cached RAG search results."""
        key = (query, n_results)
        if key in self._rag_cache:
            self._hits += 1
            logger.debug(f"RAG cache hit for query: {query[:50]}")
            return self._rag_cache[key]
        self._misses += 1
        return None

    def cache_rag_results(self, query: str, n_results: int, results: list):
        """Cache RAG search results."""
        key = (query, n_results)

        # Simple size limiting (FIFO-ish)
        if len(self._rag_cache) >= self.max_size:
            # Remove oldest entry
            self._rag_cache.pop(next(iter(self._rag_cache)))

        self._rag_cache[key] = results
        logger.debug(f"Cached RAG results for query: {query[:50]}")

    def get_combo_results(self, card_pair: tuple[str, str]):
        """Get cached combo search results for a card pair."""
        # Normalize order for consistent caching
        key = tuple(sorted(card_pair))
        if key in self._combo_cache:
            self._hits += 1
            logger.debug(f"Combo cache hit for pair: {key}")
            return self._combo_cache[key]
        self._misses += 1
        return None

    def cache_combo_results(self, card_pair: tuple[str, str], combos: list):
        """Cache combo search results for a card pair."""
        # Normalize order for consistent caching
        key = tuple(sorted(card_pair))

        # Simple size limiting
        if len(self._combo_cache) >= self.max_size * 2:  # Allow more combo cache entries
            # Remove oldest entry
            self._combo_cache.pop(next(iter(self._combo_cache)))

        self._combo_cache[key] = combos
        logger.debug(f"Cached combo results for pair: {key}")

    def clear(self):
        """Clear all caches."""
        self._rag_cache.clear()
        self._combo_cache.clear()
        self._hits = 0
        self._misses = 0
        logger.info("Cleared all suggestion caches")

    def stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0

        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "rag_cache_size": len(self._rag_cache),
            "combo_cache_size": len(self._combo_cache),
            "total_entries": len(self._rag_cache) + len(self._combo_cache),
        }


# Global cache instance
_global_cache = None


def get_suggestion_cache() -> SuggestionCache:
    """Get the global suggestion cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = SuggestionCache(max_size=128)
    return _global_cache


def clear_suggestion_cache():
    """Clear the global suggestion cache."""
    cache = get_suggestion_cache()
    cache.clear()


def get_cache_stats() -> dict[str, Any]:
    """Get statistics from the global suggestion cache."""
    cache = get_suggestion_cache()
    return cache.stats()
