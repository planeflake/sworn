"""
Cache for world entities to reduce database loads
"""
import time
from typing import Dict, Optional, Tuple
from app.game_state.models.world import WorldEntity

class WorldCache:
    """
    Cache for world entities to reduce database loads.
    
    Implements a simple in-memory cache with TTL (Time To Live) for world entities.
    """
    
    # Class-level cache, shared across all instances
    _cache: Dict[str, Tuple[WorldEntity, float]] = {}
    
    # Default TTL in seconds
    DEFAULT_TTL = 60  # 1 minute
    
    @classmethod
    def get(cls, world_id: str) -> Optional[WorldEntity]:
        """
        Get a world entity from cache if it exists and is not expired.
        
        Args:
            world_id: The ID of the world to retrieve
            
        Returns:
            The cached WorldEntity or None if not in cache or expired
        """
        if world_id not in cls._cache:
            return None
            
        world, expiry_time = cls._cache[world_id]
        
        # Check if cache entry has expired
        if expiry_time < time.time():
            # Remove expired entry
            cls._cache.pop(world_id, None)
            return None
            
        return world
    
    @classmethod
    def set(cls, world: WorldEntity, ttl: int = DEFAULT_TTL) -> None:
        """
        Add or update a world entity in the cache.
        
        Args:
            world: The WorldEntity to cache
            ttl: Time to live in seconds before the cache entry expires
        """
        expiry_time = time.time() + ttl
        cls._cache[world.world_id] = (world, expiry_time)
    
    @classmethod
    def invalidate(cls, world_id: str) -> None:
        """
        Remove a specific world from the cache.
        
        Args:
            world_id: The ID of the world to remove from cache
        """
        cls._cache.pop(world_id, None)
    
    @classmethod
    def clear(cls) -> None:
        """Clear the entire cache"""
        cls._cache.clear()
    
    @classmethod
    def get_cache_stats(cls) -> Dict:
        """Get statistics about the current cache state"""
        current_time = time.time()
        active_entries = sum(1 for _, expiry in cls._cache.values() if expiry > current_time)
        
        return {
            "total_entries": len(cls._cache),
            "active_entries": active_entries,
            "expired_entries": len(cls._cache) - active_entries
        }