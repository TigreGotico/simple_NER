"""Caching utilities for simple_NER.

This module provides caching support for NER results to improve
performance when processing the same text multiple times.
"""
from __future__ import annotations

import hashlib
import json
from collections import OrderedDict
from pathlib import Path
from typing import Any

from simple_NER import Entity


class LRUCache:
    """Least Recently Used (LRU) cache for NER results.

    Args:
        max_size: Maximum number of entries to cache.

    Example:
        ```python
        from simple_NER.utils.cache import LRUCache

        cache = LRUCache(max_size=100)
        cache.set("text1", entities)
        entities = cache.get("text1")
        ```
    """

    def __init__(self, max_size: int = 100) -> None:
        """Initialize LRU cache.

        Args:
            max_size: Maximum number of entries.
        """
        self._cache: OrderedDict[str, list[Entity]] = OrderedDict()
        self._max_size = max_size
        self._hits = 0
        self._misses = 0

    def _make_key(self, text: str) -> str:
        """Create cache key from text.

        Args:
            text: Input text.

        Returns:
            Hash key string.
        """
        return hashlib.md5(text.encode(), usedforsecurity=False).hexdigest()

    def get(self, text: str) -> list[Entity] | None:
        """Get cached entities for text.

        Args:
            text: Input text.

        Returns:
            Cached entities or None if not found.
        """
        key = self._make_key(text)
        if key in self._cache:
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._hits += 1
            return self._cache[key]
        self._misses += 1
        return None

    def set(self, text: str, entities: list[Entity]) -> None:
        """Cache entities for text.

        Args:
            text: Input text.
            entities: Entities to cache.
        """
        key = self._make_key(text)

        if key in self._cache:
            # Update existing entry
            self._cache.move_to_end(key)
            self._cache[key] = entities
        else:
            # Add new entry
            if len(self._cache) >= self._max_size:
                # Remove oldest entry
                self._cache.popitem(last=False)
            self._cache[key] = entities

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    @property
    def size(self) -> int:
        """Return current cache size."""
        return len(self._cache)

    @property
    def hit_rate(self) -> float:
        """Return cache hit rate."""
        total = self._hits + self._misses
        if total == 0:
            return 0.0
        return self._hits / total

    def stats(self) -> dict[str, Any]:
        """Return cache statistics.

        Returns:
            Dictionary with cache stats.
        """
        return {
            "size": self.size,
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self.hit_rate,
        }


class FileCache:
    """File-based cache for persisting NER results.

    Args:
        cache_dir: Directory to store cache files.
        max_size: Maximum number of entries to keep.

    Example:
        ```python
        from simple_NER.utils.cache import FileCache

        cache = FileCache(cache_dir=".ner_cache")
        cache.set("text1", entities)
        entities = cache.get("text1")
        ```
    """

    def __init__(
        self,
        cache_dir: str | Path = ".ner_cache",
        max_size: int = 1000,
    ) -> None:
        """Initialize file cache.

        Args:
            cache_dir: Directory for cache files.
            max_size: Maximum number of cache entries.
        """
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._max_size = max_size
        self._index_file = self._cache_dir / "index.json"
        self._index: dict[str, str] = self._load_index()

    def _load_index(self) -> dict[str, str]:
        """Load cache index from disk.

        Returns:
            Index dictionary mapping keys to filenames.
        """
        if self._index_file.exists():
            try:
                with open(self._index_file, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_index(self) -> None:
        """Save cache index to disk."""
        try:
            with open(self._index_file, "w", encoding="utf-8") as f:
                json.dump(self._index, f)
        except IOError:
            pass

    def _make_key(self, text: str) -> str:
        """Create cache key from text.

        Args:
            text: Input text.

        Returns:
            Hash key string.
        """
        return hashlib.sha256(text.encode(), usedforsecurity=False).hexdigest()

    def _entity_to_dict(self, entity: Entity) -> dict[str, Any]:
        """Convert Entity to dictionary for JSON serialization.

        Args:
            entity: Entity to convert.

        Returns:
            Dictionary representation.
        """
        return entity.as_json()

    def _dict_to_entity(self, data: dict[str, Any]) -> Entity:
        """Convert dictionary to Entity.

        Args:
            data: Dictionary from JSON.

        Returns:
            Entity object.
        """
        entity = Entity(
            value=data.get("value", ""),
            entity_type=data.get("entity_type", "entity"),
            source_text=data.get("source_text", ""),
            confidence=data.get("confidence", 1.0),
            data=data.get("data", {}),
        )
        return entity

    def get(self, text: str) -> list[Entity] | None:
        """Get cached entities for text.

        Args:
            text: Input text.

        Returns:
            Cached entities or None if not found.
        """
        key = self._make_key(text)
        if key not in self._index:
            return None

        cache_file = self._cache_dir / self._index[key]
        if not cache_file.exists():
            return None

        try:
            with open(cache_file, encoding="utf-8") as f:
                data = json.load(f)
                return [self._dict_to_entity(e) for e in data.get("entities", [])]
        except (json.JSONDecodeError, IOError):
            return None

    def set(self, text: str, entities: list[Entity]) -> None:
        """Cache entities for text.

        Args:
            text: Input text.
            entities: Entities to cache.
        """
        key = self._make_key(text)

        # Remove old entry if exists
        if key in self._index:
            old_file = self._cache_dir / self._index[key]
            if old_file.exists():
                old_file.unlink()

        # Create new cache file
        cache_file = self._cache_dir / f"{key}.json"
        data = {
            "text": text,
            "entities": [self._entity_to_dict(e) for e in entities],
        }

        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f)
            self._index[key] = cache_file.name

            # Enforce max size
            if len(self._index) > self._max_size:
                # Remove oldest entry
                oldest_key = next(iter(self._index))
                oldest_file = self._cache_dir / self._index[oldest_key]
                if oldest_file.exists():
                    oldest_file.unlink()
                del self._index[oldest_key]

            self._save_index()
        except IOError:
            pass

    def clear(self) -> None:
        """Clear all cached entries."""
        for key in self._index.values():
            cache_file = self._cache_dir / key
            if cache_file.exists():
                cache_file.unlink()
        self._index.clear()
        self._save_index()

    @property
    def size(self) -> int:
        """Return current cache size."""
        return len(self._index)
