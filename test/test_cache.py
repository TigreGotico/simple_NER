"""Unit tests for caching utilities: LRUCache and FileCache."""
import os
import shutil
import tempfile
from pathlib import Path

import pytest

from simple_NER import Entity
from simple_NER.utils.cache import FileCache, LRUCache


# ---------------------------------------------------------------------------
# LRUCache Tests
# ---------------------------------------------------------------------------

class TestLRUCache:
    """Tests for LRUCache."""

    def test_basic_set_get(self):
        """Test basic set and get operations."""
        cache = LRUCache(max_size=10)
        entities = [Entity("test", "test", source_text="test")]

        cache.set("key1", entities)
        result = cache.get("key1")

        assert result is not None
        assert len(result) == 1
        assert result[0].value == "test"

    def test_cache_miss(self):
        """Test cache miss returns None."""
        cache = LRUCache(max_size=10)
        result = cache.get("nonexistent")
        assert result is None

    def test_max_size_eviction(self):
        """Test that oldest entries are evicted when max size is reached."""
        cache = LRUCache(max_size=3)

        # Add 4 entries to a cache with max_size=3
        for i in range(4):
            cache.set(f"key{i}", [Entity(f"value{i}", "test", source_text="test")])

        # First entry should be evicted
        assert cache.get("key0") is None
        assert cache.get("key1") is not None
        assert cache.get("key2") is not None
        assert cache.get("key3") is not None

    def test_lru_order(self):
        """Test that recently used entries are kept."""
        cache = LRUCache(max_size=3)

        # Add entries
        cache.set("key1", [Entity("v1", "test", source_text="test")])
        cache.set("key2", [Entity("v2", "test", source_text="test")])
        cache.set("key3", [Entity("v3", "test", source_text="test")])

        # Access key1 (makes it recently used)
        cache.get("key1")

        # Add new entry - should evict key2 (oldest not recently used)
        cache.set("key4", [Entity("v4", "test", source_text="test")])

        # key1 should still be there (was accessed recently)
        assert cache.get("key1") is not None
        # key2 should be evicted
        assert cache.get("key2") is None

    def test_clear(self):
        """Test clearing the cache."""
        cache = LRUCache(max_size=10)
        cache.set("key1", [Entity("v1", "test", source_text="test")])
        cache.set("key2", [Entity("v2", "test", source_text="test")])

        cache.clear()

        assert cache.size == 0
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_stats(self):
        """Test cache statistics."""
        cache = LRUCache(max_size=10)

        # Add and retrieve (hits)
        cache.set("key1", [Entity("v1", "test", source_text="test")])
        cache.get("key1")
        cache.get("key1")

        # Misses
        cache.get("nonexistent1")
        cache.get("nonexistent2")

        stats = cache.stats()

        assert stats["size"] == 1
        assert stats["max_size"] == 10
        assert stats["hits"] == 2
        assert stats["misses"] == 2
        assert stats["hit_rate"] == 0.5  # 2 hits / 4 total

    def test_update_existing_key(self):
        """Test updating an existing key."""
        cache = LRUCache(max_size=10)

        entities1 = [Entity("v1", "test", source_text="test")]
        entities2 = [Entity("v2", "test", source_text="test")]

        cache.set("key1", entities1)
        cache.set("key1", entities2)

        result = cache.get("key1")
        assert len(result) == 1
        assert result[0].value == "v2"

    def test_same_text_different_objects(self):
        """Test caching same text multiple times."""
        cache = LRUCache(max_size=10)

        entities1 = [Entity("test", "test", source_text="test")]
        entities2 = [Entity("test2", "test", source_text="test2")]

        cache.set("text1", entities1)
        cache.set("text1", entities2)  # Should update

        result = cache.get("text1")
        assert len(result) == 1
        assert result[0].value == "test2"


# ---------------------------------------------------------------------------
# FileCache Tests
# ---------------------------------------------------------------------------

class TestFileCache:
    """Tests for FileCache."""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary cache directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_basic_set_get(self, temp_cache_dir):
        """Test basic set and get operations."""
        cache = FileCache(cache_dir=temp_cache_dir, max_size=10)
        entities = [Entity("test", "test", source_text="test")]

        cache.set("key1", entities)
        result = cache.get("key1")

        assert result is not None
        assert len(result) == 1
        assert result[0].value == "test"

    def test_cache_miss(self, temp_cache_dir):
        """Test cache miss returns None."""
        cache = FileCache(cache_dir=temp_cache_dir)
        result = cache.get("nonexistent")
        assert result is None

    def test_persistence(self, temp_cache_dir):
        """Test that cache persists after creating new instance."""
        entities = [Entity("persistent", "test", source_text="test")]

        # Write to cache
        cache1 = FileCache(cache_dir=temp_cache_dir)
        cache1.set("key1", entities)

        # Read from new instance
        cache2 = FileCache(cache_dir=temp_cache_dir)
        result = cache2.get("key1")

        assert result is not None
        assert result[0].value == "persistent"

    def test_clear(self, temp_cache_dir):
        """Test clearing the file cache."""
        cache = FileCache(cache_dir=temp_cache_dir)
        cache.set("key1", [Entity("v1", "test", source_text="test")])
        cache.set("key2", [Entity("v2", "test", source_text="test")])

        cache.clear()

        assert cache.size == 0
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_max_size_enforcement(self, temp_cache_dir):
        """Test that max size is enforced."""
        cache = FileCache(cache_dir=temp_cache_dir, max_size=3)

        # Add 5 entries
        for i in range(5):
            cache.set(f"key{i}", [Entity(f"value{i}", "test", source_text="test")])

        # Should only have 3 entries
        assert cache.size <= 3

    def test_cache_directory_creation(self, temp_cache_dir):
        """Test that cache directory is created if it doesn't exist."""
        new_dir = os.path.join(temp_cache_dir, "subdir", "cache")
        cache = FileCache(cache_dir=new_dir)

        assert os.path.exists(new_dir)
        cache.set("key1", [Entity("v1", "test", source_text="test")])
        assert cache.size == 1

    def test_different_texts_different_keys(self, temp_cache_dir):
        """Test that different texts get different cache keys."""
        cache = FileCache(cache_dir=temp_cache_dir)

        entities1 = [Entity("test1", "test", source_text="test1")]
        entities2 = [Entity("test2", "test", source_text="test2")]

        cache.set("text1", entities1)
        cache.set("text2", entities2)

        result1 = cache.get("text1")
        result2 = cache.get("text2")

        assert result1 is not None
        assert result2 is not None
        assert result1[0].value == "test1"
        assert result2[0].value == "test2"

    def test_index_file_creation(self, temp_cache_dir):
        """Test that index file is created."""
        cache = FileCache(cache_dir=temp_cache_dir)
        cache.set("key1", [Entity("v1", "test", source_text="test")])

        index_file = Path(temp_cache_dir) / "index.json"
        assert index_file.exists()
