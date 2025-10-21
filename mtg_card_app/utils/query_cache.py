"""Query result caching for improved performance."""

import hashlib
import json
import logging
from collections import OrderedDict
from typing import Any

logger = logging.getLogger(__name__)


class QueryCache:
    """LRU cache for query results with statistics tracking."""

    def __init__(self, maxsize: int = 128) -> None:
        """Initialize the query cache.

        Args:
            maxsize: Maximum number of cached queries

        """
        self.maxsize = maxsize
        self._cache: OrderedDict[str, Any] = OrderedDict()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "total_queries": 0,
        }

    def _make_key(self, query: str, filters: dict[str, Any] | None = None) -> str:
        """Create a cache key from query and filters.

        Args:
            query: Query string
            filters: Optional filters dictionary

        Returns:
            Unique cache key

        """
        # Normalize query
        normalized_query = query.lower().strip()

        # Create deterministic key from query + filters
        cache_data = {
            "query": normalized_query,
            "filters": filters or {},
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_str.encode()).hexdigest()

    def get(self, query: str, filters: dict[str, Any] | None = None) -> tuple[bool, Any]:
        """Get cached query result if available.

        Args:
            query: Query string
            filters: Optional filters

        Returns:
            Tuple of (is_cached, cached_result)

        """
        cache_key = self._make_key(query, filters)
        self._stats["total_queries"] += 1

        if cache_key in self._cache:
            # Move to end (most recently used)
            self._cache.move_to_end(cache_key)
            self._stats["hits"] += 1
            logger.debug("Cache HIT for query: %s", query[:50])
            return True, self._cache[cache_key]

        self._stats["misses"] += 1
        logger.debug("Cache MISS for query: %s", query[:50])
        return False, None

    def set(self, query: str, result: Any, filters: dict[str, Any] | None = None) -> None:
        """Cache a query result.

        Args:
            query: Query string
            result: Result to cache
            filters: Optional filters

        """
        cache_key = self._make_key(query, filters)

        # Add to cache
        self._cache[cache_key] = result
        self._cache.move_to_end(cache_key)

        # Remove oldest if over maxsize
        if len(self._cache) > self.maxsize:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            logger.debug("Evicted oldest cache entry")

        logger.debug("Cached result for query: %s", query[:50])

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache stats

        """
        hit_rate = self._stats["hits"] / self._stats["total_queries"] if self._stats["total_queries"] > 0 else 0.0

        return {
            "cache_size": self.maxsize,
            "current_size": len(self._cache),
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "total_queries": self._stats["total_queries"],
            "hit_rate": round(hit_rate, 3),
        }

    def clear(self) -> None:
        """Clear the cache."""
        self._cache.clear()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "total_queries": 0,
        }
        logger.info("Cache cleared")
