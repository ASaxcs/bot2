# short_term.py - Modul memori jangka pendek
import time
from collections import deque
from typing import Dict, List, Any

class ShortTermMemory:
    """
    Mengimplementasikan memori jangka pendek untuk menyimpan konteks percakapan terbaru
    """
    
    def __init__(self, config=None):
        """
        Inisialisasi memori jangka pendek
        
        Args:
            config: Konfigurasi untuk memori jangka pendek
        """
        if config is None:
            config = {}
            
        self.max_entries = config.get("max_entries", 20)
        self.memory = deque(maxlen=self.max_entries)
    
    def add_entry(self, entry: Dict[str, Any]):
        """
        Menambahkan entri ke memori jangka pendek
        
        Args:
            entry: Entri yang akan ditambahkan
        """
        # Tambahkan timestamp
        entry["timestamp"] = time.time()
        self.memory.append(entry)
    
    def get_recent_entries(self, n: int = None) -> List[Dict[str, Any]]:
        """
        Mendapatkan n entri terbaru dari memori
        
        Args:
            n: Jumlah entri yang akan diambil (default: semua)
            
        Returns:
            List entri memori terbaru
        """
        if n is None or n >= len(self.memory):
            return list(self.memory)
        return list(self.memory)[-n:]
    
    def clear(self):
        """Menghapus semua entri memori"""
        self.memory.clear()

