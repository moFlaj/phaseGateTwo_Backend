# app/user/services/image_cache_service.py
import time
from typing import Optional, Dict
from threading import Lock


class ImageCacheService:
    """Simple in-memory cache for signed image URLs."""
    
    def __init__(self):
        self._cache: Dict[str, tuple] = {}  # key: (url, expiration_time)
        self._lock = Lock()
        self._cleanup_interval = 300  # Clean up every 5 minutes
        self._last_cleanup = time.time()

    def get(self, s3_key: str) -> Optional[str]:
        """Get cached signed URL if it exists and hasn't expired."""
        with self._lock:
            self._cleanup_expired()
            
            if s3_key in self._cache:
                url, expiration_time = self._cache[s3_key]
                # Check if URL is still valid (with 60 second buffer)
                if time.time() < expiration_time - 60:
                    return url
                else:
                    # Remove expired entry
                    del self._cache[s3_key]
        return None

    def set(self, s3_key: str, url: str, expires_in: int = 3600) -> None:
        """Cache a signed URL with its expiration time."""
        with self._lock:
            self._cleanup_expired()
            
            expiration_time = time.time() + expires_in
            self._cache[s3_key] = (url, expiration_time)

    def _cleanup_expired(self) -> None:
        """Remove expired entries from cache."""
        current_time = time.time()
        
        # Only cleanup periodically to avoid overhead
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
            
        expired_keys = [
            key for key, (_, expiration_time) in self._cache.items()
            if current_time >= expiration_time
        ]
        
        for key in expired_keys:
            del self._cache[key]
            
        self._last_cleanup = current_time

    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()


# Global instance
image_cache = ImageCacheService()