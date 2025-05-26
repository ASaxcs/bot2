# short_term.py - Fixed Short Term Memory Module
import time
from collections import deque
from typing import Dict, List, Any, Union

class ShortTermMemory:
    """
    Implements short-term memory for storing recent conversation context
    """
    
    def __init__(self, config=None):
        """
        Initialize short-term memory
        
        Args:
            config: Configuration for short-term memory
        """
        if config is None:
            config = {}
            
        self.max_entries = config.get("max_entries", 20)
        self.memories = deque(maxlen=self.max_entries)  # Changed from 'memory' to 'memories'
        self.importance_threshold = config.get("importance_threshold", 0.3)
    
    def add_memory(self, entry: Union[Dict, str], content_type: str = None, importance: float = 1.0):
        """
        Add entry to short-term memory.
        
        Supports multiple calling patterns:
        1. add_memory({"content": "text", "type": "user"}, importance=1.0)
        2. add_memory("text", "user_input", importance=1.0)  # Legacy support
        3. add_memory({"content": "text", "type": "user_input"}, "user_input", importance=1.0)

        Args:
            entry: Data to be stored (dict or string)
            content_type: Content type (optional, for backward compatibility)
            importance (float): Memory importance level (default: 1.0)
        """
        try:
            # Handle legacy calling pattern: add_memory(content, type, importance)
            if isinstance(entry, str) and content_type is not None:
                memory_entry = {
                    "content": entry,
                    "type": content_type
                }
            # Handle dict entry
            elif isinstance(entry, dict):
                memory_entry = entry.copy()
                # If content_type is provided as second parameter, use it
                if content_type is not None:
                    memory_entry["type"] = content_type
            else:
                # Fallback for other types
                memory_entry = {
                    "content": str(entry),
                    "type": content_type or "unknown"
                }
            
            # Add metadata
            memory_entry["timestamp"] = time.time()
            memory_entry["importance"] = importance
            
            # Add formatted timestamp for readability
            from datetime import datetime
            memory_entry["formatted_time"] = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")
            
            self.memories.append(memory_entry)
            
        except Exception as e:
            print(f"Error in add_memory: {e}")
            print(f"Entry: {entry}")
            print(f"Content type: {content_type}")
            print(f"Importance: {importance}")
            # Don't raise the exception, just add a basic entry
            self.memories.append({
                "content": str(entry),
                "type": content_type or "error",
                "timestamp": time.time(),
                "importance": importance,
                "error": str(e)
            })
    
    def get_recent_entries(self, n: int = None) -> List[Dict[str, Any]]:
        """
        Get n recent entries from memory
        
        Args:
            n: Number of entries to retrieve (default: all)
            
        Returns:
            List of recent memory entries
        """
        if n is None or n >= len(self.memories):
            return list(self.memories)
        return list(self.memories)[-n:]
    
    def get_recent_memories(self, n: int = None) -> List[Dict[str, Any]]:
        """
        Alias for get_recent_entries to maintain compatibility
        
        Args:
            n: Number of entries to retrieve (default: all)
            
        Returns:
            List of recent memory entries
        """
        return self.get_recent_entries(n)
    
    def get_memories_by_type(self, memory_type: str) -> List[Dict[str, Any]]:
        """
        Get memories filtered by type
        
        Args:
            memory_type: Type of memory to filter by
            
        Returns:
            List of memories of the specified type
        """
        return [memory for memory in self.memories if memory.get("type") == memory_type]
    
    def get_important_memories(self, threshold: float = None) -> List[Dict[str, Any]]:
        """
        Get memories above importance threshold
        
        Args:
            threshold: Importance threshold (default: use configured threshold)
            
        Returns:
            List of important memories
        """
        if threshold is None:
            threshold = self.importance_threshold
        
        return [memory for memory in self.memories if memory.get("importance", 0) >= threshold]
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """
        Get summary of memory contents
        
        Returns:
            Dictionary with memory statistics
        """
        if not self.memories:
            return {
                "total_memories": 0,
                "memory_types": {},
                "importance_stats": {"min": 0, "max": 0, "avg": 0},
                "time_range": None
            }
        
        # Count by type
        type_counts = {}
        importances = []
        timestamps = []
        
        for memory in self.memories:
            mem_type = memory.get("type", "unknown")
            type_counts[mem_type] = type_counts.get(mem_type, 0) + 1
            importances.append(memory.get("importance", 0))
            timestamps.append(memory.get("timestamp", 0))
        
        return {
            "total_memories": len(self.memories),
            "memory_types": type_counts,
            "importance_stats": {
                "min": min(importances),
                "max": max(importances),
                "avg": sum(importances) / len(importances)
            },
            "time_range": {
                "oldest": min(timestamps),
                "newest": max(timestamps)
            } if timestamps else None
        }
    
    def search_memories(self, query: str) -> List[Dict[str, Any]]:
        """
        Search memories by content
        
        Args:
            query: Search query
            
        Returns:
            List of matching memories
        """
        query_lower = query.lower()
        matching_memories = []
        
        for memory in self.memories:
            content = str(memory.get("content", "")).lower()
            if query_lower in content:
                matching_memories.append(memory)
        
        return matching_memories
    
    def clear(self):
        """Clear all memory entries"""
        self.memories.clear()
    
    def __len__(self):
        """Return number of memories"""
        return len(self.memories)
    
    def __bool__(self):
        """Return True if there are memories"""
        return len(self.memories) > 0