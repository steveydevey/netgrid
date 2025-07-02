"""
Cache management utilities for NetGrid.

This module provides general caching functionality that can be used across
the NetGrid project for various caching needs.
"""

import os
import json
import pickle
import hashlib
import time
from typing import Any, Dict, Optional, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """
    General cache manager for NetGrid.
    
    Provides file-based caching with TTL (Time To Live) support and
    automatic cache invalidation.
    """
    
    def __init__(self, cache_dir: Optional[str] = None, default_ttl: int = 3600):
        """
        Initialize the cache manager.
        
        Args:
            cache_dir: Directory to store cache files. Defaults to ~/.netgrid/cache
            default_ttl: Default time to live in seconds (1 hour)
        """
        if cache_dir is None:
            cache_dir = os.path.expanduser("~/.netgrid/cache")
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl
    
    def _get_cache_key(self, key: str) -> str:
        """
        Generate a cache key hash.
        
        Args:
            key: Original key string
            
        Returns:
            Hashed cache key
        """
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_cache_file(self, key: str, suffix: str = "json") -> Path:
        """
        Get cache file path for a key.
        
        Args:
            key: Cache key
            suffix: File suffix (json, pickle, etc.)
            
        Returns:
            Path to cache file
        """
        cache_key = self._get_cache_key(key)
        return self.cache_dir / f"{cache_key}.{suffix}"
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from cache.
        
        Args:
            key: Cache key
            default: Default value if key not found or expired
            
        Returns:
            Cached value or default
        """
        cache_file = self._get_cache_file(key)
        
        if not cache_file.exists():
            return default
        
        try:
            # Check if cache is expired
            if self._is_expired(cache_file):
                cache_file.unlink()
                return default
            
            # Load cached data
            with open(cache_file, 'r') as f:
                data = json.load(f)
                return data.get('value', default)
                
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load cache for key '{key}': {e}")
            # Remove corrupted cache file
            if cache_file.exists():
                cache_file.unlink()
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set a value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses default if None)
            
        Returns:
            True if successful, False otherwise
        """
        if ttl is None:
            ttl = self.default_ttl
        
        cache_file = self._get_cache_file(key)
        
        try:
            # Prepare cache data with metadata
            cache_data = {
                'value': value,
                'created_at': time.time(),
                'ttl': ttl
            }
            
            # Save to cache file
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            return True
            
        except (TypeError, IOError) as e:
            logger.error(f"Failed to save cache for key '{key}': {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        cache_file = self._get_cache_file(key)
        
        if cache_file.exists():
            try:
                cache_file.unlink()
                return True
            except IOError as e:
                logger.warning(f"Failed to delete cache for key '{key}': {e}")
                return False
        
        return False
    
    def exists(self, key: str) -> bool:
        """
        Check if a key exists in cache and is not expired.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists and is valid, False otherwise
        """
        cache_file = self._get_cache_file(key)
        
        if not cache_file.exists():
            return False
        
        return not self._is_expired(cache_file)
    
    def _is_expired(self, cache_file: Path) -> bool:
        """
        Check if a cache file is expired.
        
        Args:
            cache_file: Path to cache file
            
        Returns:
            True if expired, False otherwise
        """
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
                
            created_at = data.get('created_at', 0)
            ttl = data.get('ttl', self.default_ttl)
            
            return time.time() - created_at > ttl
            
        except (json.JSONDecodeError, IOError):
            return True
    
    def clear(self, pattern: Optional[str] = None) -> int:
        """
        Clear cache files.
        
        Args:
            pattern: Optional glob pattern to match files (e.g., "*.json")
            
        Returns:
            Number of files deleted
        """
        deleted_count = 0
        
        if pattern:
            files = list(self.cache_dir.glob(pattern))
        else:
            files = list(self.cache_dir.glob("*"))
        
        for file_path in files:
            if file_path.is_file():
                try:
                    file_path.unlink()
                    deleted_count += 1
                except IOError as e:
                    logger.warning(f"Failed to delete cache file {file_path}: {e}")
        
        return deleted_count
    
    def get_stats(self) -> Dict[str, Union[int, float]]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_files = 0
        total_size = 0
        expired_files = 0
        
        for file_path in self.cache_dir.glob("*"):
            if file_path.is_file():
                total_files += 1
                total_size += file_path.stat().st_size
                
                if self._is_expired(file_path):
                    expired_files += 1
        
        return {
            'total_files': total_files,
            'total_size_bytes': total_size,
            'expired_files': expired_files,
            'cache_dir': str(self.cache_dir)
        }
    
    def cleanup_expired(self) -> int:
        """
        Remove expired cache files.
        
        Returns:
            Number of expired files removed
        """
        removed_count = 0
        
        for file_path in self.cache_dir.glob("*"):
            if file_path.is_file() and self._is_expired(file_path):
                try:
                    file_path.unlink()
                    removed_count += 1
                except IOError as e:
                    logger.warning(f"Failed to delete expired cache file {file_path}: {e}")
        
        return removed_count


class MemoryCache:
    """
    Simple in-memory cache with TTL support.
    
    Useful for temporary caching during program execution.
    """
    
    def __init__(self, default_ttl: int = 300):
        """
        Initialize memory cache.
        
        Args:
            default_ttl: Default time to live in seconds (5 minutes)
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from memory cache.
        
        Args:
            key: Cache key
            default: Default value if key not found or expired
            
        Returns:
            Cached value or default
        """
        if key not in self.cache:
            return default
        
        cache_entry = self.cache[key]
        
        # Check if expired
        if time.time() - cache_entry['created_at'] > cache_entry['ttl']:
            del self.cache[key]
            return default
        
        return cache_entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in memory cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses default if None)
        """
        if ttl is None:
            ttl = self.default_ttl
        
        self.cache[key] = {
            'value': value,
            'created_at': time.time(),
            'ttl': ttl
        }
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from memory cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cached values."""
        self.cache.clear()
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get memory cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            'total_entries': len(self.cache),
            'default_ttl': self.default_ttl
        } 