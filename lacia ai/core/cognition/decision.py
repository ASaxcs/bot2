#!/usr/bin/env python3
# decision.py - Modul pengambilan keputusan LACIA AI

from typing import Dict, Any, List

class DecisionEngine:
    """
    Mesin pengambilan keputusan untuk LACIA AI
    """
    
    def __init__(self, config):
        """
        Inisialisasi mesin pengambilan keputusan
        
        Args:
            config: Konfigurasi sistem
        """
        self.config = config
        self.importance_threshold = config.get("decision", {}).get("importance_threshold", 0.6)
    
    def should_store_long_term(self, user_input: str, response: str) -> bool:
        """
        Menentukan apakah interaksi perlu disimpan dalam memori jangka panjang
        
        Args:
            user_input: Input dari pengguna
            response: Respons dari sistem
            
        Returns:
            bool: True jika perlu disimpan, False jika tidak
        """
        # Hitung skor kepentingan berdasarkan beberapa faktor
        importance_score = self._calculate_importance(user_input, response)
        
        return importance_score >= self.importance_threshold
    
    def _calculate_importance(self, user_input: str, response: str) -> float:
        """
        Menghitung skor kepentingan dari interaksi
        
        Args:
            user_input: Input dari pengguna
            response: Respons dari sistem
            
        Returns:
            float: Skor kepentingan (0.0-1.0)
        """
        score = 0.0
        
        # Faktor 1: Panjang input (input yang lebih panjang mungkin lebih penting)
        input_length = len(user_input)
        if input_length > 100:
            score += 0.3
        elif input_length > 50:
            score += 0.2
        elif input_length > 20:
            score += 0.1
            
        # Faktor 2: Adanya kata-kata kunci tertentu
        important_keywords = [
            "penting", "ingat", "simpan", "catat", "jangan lupa",
            "jadwal", "tanggal", "waktu", "rencana", "proyek",
            "nama", "kontak", "alamat", "email", "telepon",
            "password", "kata sandi"
        ]
        
        # Hitung berapa kata kunci yang muncul
        keyword_count = sum(1 for keyword in important_keywords if keyword.lower() in user_input.lower())
        keyword_score = min(0.4, keyword_count * 0.1)  # Maksimum 0.4
        score += keyword_score
        
        # Faktor 3: Apakah ada pertanyaan
        if "?" in user_input:
            score += 0.1
            
        # Faktor 4: Tanda tanya/seru berulang sebagai indikator emosi/urgensi
        if "??" in user_input or "!!" in user_input:
            score += 0.1
            
        # Faktor 5: Deteksi instruksi (kata kerja di awal kalimat)
        instruction_verbs = [
            "tolong", "bantu", "buat", "cari", "temukan", "jelaskan",
            "analisis", "rangkum", "catat", "ingat", "simpan"
        ]
        
        first_word = user_input.lower().split()[0] if user_input else ""
        if first_word in instruction_verbs:
            score += 0.2
            
        return score
    
    def select_response_strategy(self, user_input: str, context: Dict[str, Any]) -> str:
        """
        Memilih strategi respons berdasarkan input pengguna dan konteks
        
        Args:
            user_input: Input dari pengguna
            context: Konteks percakapan dan sistem
            
        Returns:
            str: Strategi respons yang dipilih
        """
        # Implementasi sederhana - logika yang lebih kompleks dapat ditambahkan nanti
        
        # Deteksi tipe kueri
        input_lower = user_input.lower()
        
        # Pertanyaan faktual
        if any(q in input_lower for q in ["apa", "siapa", "kapan", "di mana", "mengapa", "bagaimana"]):
            if len(input_lower) < 20:
                return "short_factual"
            else:
                return "detailed_explanation"
                
        # Permintaan tugas
        elif any(v in input_lower for v in ["tolong", "bantu", "buat", "cari", "bisakah"]):
            if "analisis" in input_lower or "analisa" in input_lower:
                return "analytical"
            else:
                return "task_focused"
                
        # Percakapan biasa
        elif len(user_input) < 20:
            return "casual_conversation"
            
        # Default - respons seimbang
        return "balanced"
    
    def prioritize_skills(self, user_input: str) -> List[str]:
        """
        Memprioritaskan keterampilan yang perlu digunakan berdasarkan input
        
        Args:
            user_input: Input dari pengguna
            
        Returns:
            List[str]: Daftar keterampilan yang diprioritaskan
        """
        skills = []
        input_lower = user_input.lower()
        
        # Deteksi beberapa kata kunci untuk keterampilan khusus
        if any(word in input_lower for word in ["terjemahkan", "translate", "bahasa"]):
            skills.append("translation")
            
        if any(word in input_lower for word in ["jadwal", "schedule", "acara", "reminder"]):
            skills.append("scheduling")
            
        if any(word in input_lower for word in ["hack", "retas", "analisis keamanan"]):
            skills.append("analog_hack")
            
        # Keterampilan default
        skills.append("conversation")
        
        return skills