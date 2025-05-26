# long_term.py - Fixed Long Term Memory Module
import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class LongTermMemory:
    """
    Implements long-term memory with persistent storage
    """
    
    def __init__(self, config=None):
        """
        Initialize long-term memory
        
        Args:
            config: Configuration for long-term memory
        """
        if config is None:
            config = {}
            
        self.storage_dir = config.get("storage_dir", "./data/long_term_memory")
        Path(self.storage_dir).mkdir(parents=True, exist_ok=True)
        
        # File for storing memory index
        self.index_file = os.path.join(self.storage_dir, "memory_index.json")
        self.memory_index = self._load_index()
        
        # Configuration
        self.max_keyword_length = config.get("max_keyword_length", 10)
        self.min_keyword_length = config.get("min_keyword_length", 3)
        
        # Common words to exclude from keywords (multilingual)
        self.common_words = {
            'dan', 'atau', 'dengan', 'yang', 'ini', 'itu', 'di', 'ke', 'dari', 'untuk', 'pada', 'adalah',
            'the', 'and', 'or', 'with', 'that', 'this', 'it', 'to', 'from', 'for', 'on', 'is', 'a', 'an',
            'in', 'at', 'by', 'as', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'can', 'may', 'might', 'must', 'shall'
        }
    
    def _load_index(self) -> Dict:
        """
        Load memory index from disk
        
        Returns:
            Memory index dictionary
        """
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                    # Ensure the index has the expected structure
                    if "entries" not in index_data:
                        index_data["entries"] = []
                    return index_data
            except Exception as e:
                print(f"Error loading memory index: {e}")
                return {"entries": [], "metadata": {"created": time.time()}}
        else:
            return {"entries": [], "metadata": {"created": time.time()}}
    
    def _save_index(self):
        """Save memory index to disk"""
        try:
            # Update metadata
            self.memory_index["metadata"] = self.memory_index.get("metadata", {})
            self.memory_index["metadata"]["last_updated"] = time.time()
            self.memory_index["metadata"]["total_entries"] = len(self.memory_index["entries"])
            
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory_index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving memory index: {e}")
    
    def store_interaction(self, user_input: str, response: str, context: Optional[Dict] = None):
        """
        Store interaction in long-term memory
        
        Args:
            user_input: Input from user
            response: System response
            context: Additional context information
        """
        if context is None:
            context = {}
            
        timestamp = time.time()
        date_str = datetime.fromtimestamp(timestamp).strftime("%Y%m%d_%H%M%S")
        
        # Create unique filename for this memory entry
        memory_id = f"memory_{date_str}_{len(self.memory_index['entries'])}"
        memory_file = f"{memory_id}.json"
        file_path = os.path.join(self.storage_dir, memory_file)
        
        # Create memory entry
        memory_entry = {
            "id": memory_id,
            "user_input": user_input,
            "response": response,
            "context": context,
            "timestamp": timestamp,
            "date": datetime.fromtimestamp(timestamp).isoformat(),
            "formatted_date": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Extract keywords for searching
        keywords = self._extract_keywords(user_input + " " + response)
        memory_entry["keywords"] = keywords
        
        # Calculate importance score
        importance_score = self._calculate_importance(user_input, response, context)
        memory_entry["importance"] = importance_score
        
        # Save memory to file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(memory_entry, f, ensure_ascii=False, indent=2)
                
            # Update index
            index_entry = {
                "id": memory_id,
                "file": memory_file,
                "timestamp": timestamp,
                "keywords": keywords,
                "importance": importance_score,
                "preview": user_input[:100] + "..." if len(user_input) > 100 else user_input,
                "response_preview": response[:100] + "..." if len(response) > 100 else response
            }
            
            self.memory_index["entries"].append(index_entry)
            self._save_index()
            
            print(f"✅ Memory stored: {memory_id}")
            
        except Exception as e:
            print(f"Error storing memory entry: {e}")
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text
        
        Args:
            text: Text for keyword extraction
            
        Returns:
            List of keywords
        """
        if not text:
            return []
        
        # Simple implementation - remove common words and get unique words
        words = text.lower().replace('.', ' ').replace(',', ' ').replace('!', ' ').replace('?', ' ').split()
        keywords = []
        
        for word in words:
            # Clean word
            clean_word = ''.join(c for c in word if c.isalnum())
            
            # Filter by length and common words
            if (len(clean_word) >= self.min_keyword_length and 
                clean_word not in self.common_words and
                clean_word not in keywords):
                keywords.append(clean_word)
        
        return keywords[:self.max_keyword_length]
    
    def _calculate_importance(self, user_input: str, response: str, context: Dict) -> float:
        """
        Calculate importance score for a memory
        
        Args:
            user_input: User input
            response: System response
            context: Context information
            
        Returns:
            Importance score (0.0 to 1.0)
        """
        importance = 0.5  # Base importance
        
        # Check for importance indicators in text
        importance_keywords = [
            'remember', 'important', 'significant', 'crucial', 'critical',
            'personal', 'preference', 'like', 'dislike', 'favorite', 'hate',
            'always', 'never', 'usually', 'typically', 'generally',
            'ingat', 'penting', 'signifikan', 'krusial', 'pribadi', 'suka', 'tidak suka'
        ]
        
        combined_text = (user_input + " " + response).lower()
        
        # Increase importance based on keywords
        keyword_matches = sum(1 for keyword in importance_keywords if keyword in combined_text)
        importance += min(keyword_matches * 0.1, 0.3)
        
        # Check context for importance indicators
        if context:
            emotion_state = context.get('emotion', {})
            if emotion_state.get('intensity', 0) > 0.7:
                importance += 0.1
            
            personality_context = context.get('personality', {})
            if any(level > 0.8 for level in personality_context.values()):
                importance += 0.1
        
        # Length-based importance (longer interactions might be more important)
        total_length = len(user_input) + len(response)
        if total_length > 200:
            importance += 0.1
        
        return min(importance, 1.0)
    
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search memories based on query
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        if not query:
            return []
        
        query_keywords = self._extract_keywords(query)
        if not query_keywords:
            return []
        
        results = []
        for entry in self.memory_index["entries"]:
            # Calculate match score
            match_score = 0
            entry_keywords = entry.get("keywords", [])
            
            for q_keyword in query_keywords:
                for e_keyword in entry_keywords:
                    if q_keyword in e_keyword or e_keyword in q_keyword:
                        match_score += 1
            
            # Also check preview text
            preview_text = (entry.get("preview", "") + " " + entry.get("response_preview", "")).lower()
            for q_keyword in query_keywords:
                if q_keyword in preview_text:
                    match_score += 0.5
            
            if match_score > 0:
                results.append({
                    "entry": entry,
                    "score": match_score,
                    "relevance": match_score / len(query_keywords)
                })
        
        # Sort by score and importance
        results.sort(key=lambda x: (x["score"], x["entry"].get("importance", 0)), reverse=True)
        
        # Load full content for top results
        top_results = []
        for result in results[:limit]:
            file_path = os.path.join(self.storage_dir, result["entry"]["file"])
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        memory_content = json.load(f)
                        memory_content["match_score"] = result["score"]
                        memory_content["relevance"] = result["relevance"]
                        top_results.append(memory_content)
                except Exception as e:
                    print(f"Error loading memory content: {e}")
                    
        return top_results
    
    def get_recent_memories(self, limit: int = 10) -> List[Dict]:
        """
        Get most recent memories
        
        Args:
            limit: Maximum number of memories to return
            
        Returns:
            List of recent memories
        """
        # Sort entries by timestamp (most recent first)
        sorted_entries = sorted(
            self.memory_index["entries"], 
            key=lambda x: x.get("timestamp", 0), 
            reverse=True
        )
        
        recent_memories = []
        for entry in sorted_entries[:limit]:
            file_path = os.path.join(self.storage_dir, entry["file"])
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        memory_content = json.load(f)
                        recent_memories.append(memory_content)
                except Exception as e:
                    print(f"Error loading memory content: {e}")
        
        return recent_memories
    
    def get_important_memories(self, threshold: float = 0.7, limit: int = 10) -> List[Dict]:
        """
        Get memories above importance threshold
        
        Args:
            threshold: Importance threshold
            limit: Maximum number of memories to return
            
        Returns:
            List of important memories
        """
        # Filter and sort by importance
        important_entries = [
            entry for entry in self.memory_index["entries"] 
            if entry.get("importance", 0) >= threshold
        ]
        important_entries.sort(key=lambda x: x.get("importance", 0), reverse=True)
        
        important_memories = []
        for entry in important_entries[:limit]:
            file_path = os.path.join(self.storage_dir, entry["file"])
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        memory_content = json.load(f)
                        important_memories.append(memory_content)
                except Exception as e:
                    print(f"Error loading memory content: {e}")
        
        return important_memories
    
    def get_memory_count(self) -> int:
        """
        Get total number of stored memories
        
        Returns:
            Number of memories
        """
        return len(self.memory_index["entries"])
    
    def get_memory_stats(self) -> Dict:
        """
        Get memory statistics
        
        Returns:
            Dictionary with memory statistics
        """
        if not self.memory_index["entries"]:
            return {
                "total_memories": 0,
                "storage_size": 0,
                "importance_distribution": {},
                "keyword_frequency": {},
                "date_range": None
            }
        
        entries = self.memory_index["entries"]
        
        # Calculate storage size
        storage_size = 0
        for entry in entries:
            file_path = os.path.join(self.storage_dir, entry["file"])
            if os.path.exists(file_path):
                storage_size += os.path.getsize(file_path)
        
        # Importance distribution
        importance_ranges = {"low": 0, "medium": 0, "high": 0}
        for entry in entries:
            importance = entry.get("importance", 0)
            if importance < 0.4:
                importance_ranges["low"] += 1
            elif importance < 0.7:
                importance_ranges["medium"] += 1
            else:
                importance_ranges["high"] += 1
        
        # Keyword frequency
        keyword_freq = {}
        for entry in entries:
            for keyword in entry.get("keywords", []):
                keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
        
        # Sort keywords by frequency
        top_keywords = dict(sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:20])
        
        # Date range
        timestamps = [entry.get("timestamp", 0) for entry in entries]
        date_range = None
        if timestamps:
            min_time = min(timestamps)
            max_time = max(timestamps)
            date_range = {
                "oldest": datetime.fromtimestamp(min_time).isoformat(),
                "newest": datetime.fromtimestamp(max_time).isoformat(),
                "span_days": (max_time - min_time) / (24 * 3600)
            }
        
        return {
            "total_memories": len(entries),
            "storage_size": storage_size,
            "storage_size_mb": round(storage_size / (1024 * 1024), 2),
            "importance_distribution": importance_ranges,
            "top_keywords": top_keywords,
            "date_range": date_range
        }
    
    def cleanup_old_memories(self, days_to_keep: int = 30, importance_threshold: float = 0.3):
        """
        Clean up old, low-importance memories
        
        Args:
            days_to_keep: Number of days to keep memories
            importance_threshold: Keep memories above this importance regardless of age
        """
        current_time = time.time()
        cutoff_time = current_time - (days_to_keep * 24 * 3600)
        
        entries_to_remove = []
        
        for i, entry in enumerate(self.memory_index["entries"]):
            entry_time = entry.get("timestamp", 0)
            entry_importance = entry.get("importance", 0)
            
            # Remove if old and not important
            if entry_time < cutoff_time and entry_importance < importance_threshold:
                entries_to_remove.append(i)
                
                # Delete the file
                file_path = os.path.join(self.storage_dir, entry["file"])
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"🗑️ Cleaned up memory: {entry['id']}")
                except Exception as e:
                    print(f"Error cleaning up memory file: {e}")
        
        # Remove entries from index (in reverse order to maintain indices)
        for i in reversed(entries_to_remove):
            del self.memory_index["entries"][i]
        
        if entries_to_remove:
            self._save_index()
            print(f"🧹 Cleaned up {len(entries_to_remove)} old memories")
    
    def export_memories(self, output_file: str, format: str = "json"):
        """
        Export all memories to a file
        
        Args:
            output_file: Output file path
            format: Export format ("json" or "txt")
        """
        try:
            all_memories = []
            
            for entry in self.memory_index["entries"]:
                file_path = os.path.join(self.storage_dir, entry["file"])
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        memory_content = json.load(f)
                        all_memories.append(memory_content)
            
            if format.lower() == "json":
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(all_memories, f, ensure_ascii=False, indent=2)
            elif format.lower() == "txt":
                with open(output_file, 'w', encoding='utf-8') as f:
                    for memory in all_memories:
                        f.write(f"Date: {memory.get('formatted_date', 'Unknown')}\n")
                        f.write(f"User: {memory.get('user_input', '')}\n")
                        f.write(f"AI: {memory.get('response', '')}\n")
                        f.write(f"Keywords: {', '.join(memory.get('keywords', []))}\n")
                        f.write(f"Importance: {memory.get('importance', 0):.2f}\n")
                        f.write("-" * 80 + "\n\n")
            
            print(f"✅ Exported {len(all_memories)} memories to {output_file}")
            
        except Exception as e:
            print(f"Error exporting memories: {e}")