
# long_term.py - Modul memori jangka panjang
import os
import json
import time
from datetime import datetime
from pathlib import Path

class LongTermMemory:
    """
    Mengimplementasikan memori jangka panjang dengan penyimpanan persisten
    """
    
    def __init__(self, config=None):
        """
        Inisialisasi memori jangka panjang
        
        Args:
            config: Konfigurasi untuk memori jangka panjang
        """
        if config is None:
            config = {}
            
        self.storage_dir = config.get("storage_dir", "./lacia_ai/data/knowledge_cache")
        Path(self.storage_dir).mkdir(parents=True, exist_ok=True)
        
        # File untuk menyimpan indeks memori
        self.index_file = os.path.join(self.storage_dir, "memory_index.json")
        self.memory_index = self._load_index()
    
    def _load_index(self):
        """
        Memuat indeks memori dari disk
        
        Returns:
            Dict indeks memori
        """
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error memuat indeks memori: {e}")
                return {"entries": []}
        else:
            return {"entries": []}
    
    def _save_index(self):
        """Menyimpan indeks memori ke disk"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory_index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error menyimpan indeks memori: {e}")
    
    def store_interaction(self, user_input, response, context=None):
        """
        Menyimpan interaksi ke memori jangka panjang
        
        Args:
            user_input: Input dari pengguna
            response: Respons dari sistem
            context: Informasi konteks tambahan
        """
        if context is None:
            context = {}
            
        timestamp = time.time()
        date_str = datetime.fromtimestamp(timestamp).strftime("%Y%m%d_%H%M%S")
        
        # Buat nama file untuk entri memori ini
        memory_file = f"memory_{date_str}.json"
        file_path = os.path.join(self.storage_dir, memory_file)
        
        # Buat entri memori
        memory_entry = {
            "user_input": user_input,
            "response": response,
            "context": context,
            "timestamp": timestamp,
            "date": datetime.fromtimestamp(timestamp).isoformat()
        }
        
        # Tambahkan beberapa kata kunci sederhana untuk pencarian
        keywords = self._extract_keywords(user_input)
        memory_entry["keywords"] = keywords
        
        # Simpan memori ke file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(memory_entry, f, ensure_ascii=False, indent=2)
                
            # Perbarui indeks
            index_entry = {
                "file": memory_file,
                "timestamp": timestamp,
                "keywords": keywords,
                "preview": user_input[:50] + "..." if len(user_input) > 50 else user_input
            }
            
            self.memory_index["entries"].append(index_entry)
            self._save_index()
            
        except Exception as e:
            print(f"Error menyimpan entri memori: {e}")
    
    def _extract_keywords(self, text):
        """
        Ekstrak kata kunci sederhana dari teks
        
        Args:
            text: Teks untuk ekstraksi kata kunci
            
        Returns:
            List kata kunci
        """
        # Implementasi sederhana - hilangkan kata umum dan ambil kata-kata unik
        common_words = {'dan', 'atau', 'dengan', 'yang', 'ini', 'itu', 'di', 'ke', 'dari', 'untuk', 'pada', 'adalah'}
        words = text.lower().split()
        return list(set(word for word in words if len(word) > 3 and word not in common_words))[:10]
    
    def search(self, query, limit=5):
        """
        Mencari memori berdasarkan kueri
        
        Args:
            query: Kueri pencarian
            limit: Batas jumlah hasil
            
        Returns:
            List hasil pencarian
        """
        query_keywords = self._extract_keywords(query)
        
        results = []
        for entry in self.memory_index["entries"]:
            # Hitung skor kecocokan sederhana
            match_score = sum(1 for keyword in query_keywords if keyword in entry["keywords"])
            if match_score > 0:
                results.append({
                    "entry": entry,
                    "score": match_score
                })
        
        # Urutkan berdasarkan skor kecocokan
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Ambil hasil terbaik dan muat isinya
        top_results = []
        for result in results[:limit]:
            file_path = os.path.join(self.storage_dir, result["entry"]["file"])
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        memory_content = json.load(f)
                        top_results.append(memory_content)
                except Exception as e:
                    print(f"Error memuat konten memori: {e}")
                    
        return top_results
