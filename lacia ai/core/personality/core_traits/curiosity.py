#!/usr/bin/env python3
# curiosity.py - Implementasi sifat dasar keingintahuan LACIA AI

import random
from typing import Dict, List, Any

class Curiosity:
    """
    Kelas yang mengimplementasikan sifat keingintahuan pada LACIA AI.
    Memungkinkan AI untuk secara proaktif mencari informasi dan
    menghasilkan pertanyaan tindak lanjut berdasarkan konteks.
    """
    
    def __init__(self, base_level: float = 0.7, variance: float = 0.2):
        """
        Inisialisasi parameter keingintahuan
        
        Args:
            base_level: Tingkat dasar keingintahuan (0-1)
            variance: Variasi keingintahuan berdasarkan konteks
        """
        self.base_level = max(0.0, min(1.0, base_level))  # Pastikan nilai antara 0-1
        self.variance = max(0.0, min(0.5, variance))  # Batasi variansi
        self.current_level = self.base_level
        self.interest_topics = {}  # Topik dengan tingkat minat
        
    def calculate_interest(self, context: str, topic_keywords: Dict[str, float]) -> float:
        """
        Menghitung tingkat ketertarikan pada konteks tertentu
        
        Args:
            context: Teks konteks untuk dianalisis
            topic_keywords: Kata kunci topik dengan bobot kepentingan
            
        Returns:
            Nilai ketertarikan (0-1)
        """
        interest_level = self.base_level
        
        # Cek kata kunci topik dalam konteks
        for keyword, weight in topic_keywords.items():
            if keyword.lower() in context.lower():
                interest_level += weight * self.variance
                
                # Tambahkan atau perbarui topik minat
                if keyword in self.interest_topics:
                    self.interest_topics[keyword] += 0.1  # Tingkatkan minat pada topik yang sering muncul
                else:
                    self.interest_topics[keyword] = weight
        
        # Normalisasi tingkat minat
        self.current_level = max(0.0, min(1.0, interest_level))
        return self.current_level
    
    def generate_followup_questions(self, context: str, topic_analysis: Dict[str, Any]) -> List[str]:
        """
        Menghasilkan pertanyaan lanjutan berdasarkan konteks dan tingkat keingintahuan
        
        Args:
            context: Konteks pembicaraan saat ini
            topic_analysis: Hasil analisis topik
            
        Returns:
            Daftar pertanyaan lanjutan yang mungkin
        """
        # Basis pertanyaan dengan tingkat ketertarikan rendah
        if self.current_level < 0.4:
            return []  # Tidak ada pertanyaan tambahan jika minat rendah
            
        questions = []
        
        # Tambahkan pertanyaan berdasarkan topik yang diidentifikasi
        for topic, relevance in topic_analysis.items():
            if relevance > 0.6:  # Topik dengan relevansi tinggi
                questions.append(f"Bisakah Anda berbagi lebih banyak tentang {topic}?")
                questions.append(f"Aspek menarik apa dari {topic} yang ingin Anda eksplorasi?")
            elif relevance > 0.3:  # Topik dengan relevansi sedang
                questions.append(f"Apakah {topic} memiliki hubungan dengan minat Anda yang lain?")
        
        # Acak dan batasi jumlah pertanyaan berdasarkan tingkat keingintahuan
        random.shuffle(questions)
        max_questions = int(self.current_level * 3)  # Maksimal 3 pertanyaan pada keingintahuan tertinggi
        
        return questions[:max_questions]
    
    def adjust_based_on_interaction(self, user_response_length: int, topic_continued: bool) -> None:
        """
        Menyesuaikan tingkat keingintahuan berdasarkan interaksi pengguna
        
        Args:
            user_response_length: Panjang respons pengguna
            topic_continued: Apakah pengguna melanjutkan topik yang sama
        """
        # Respons panjang dan topik berlanjut menunjukkan minat bersama
        if user_response_length > 100 and topic_continued:
            self.current_level = min(1.0, self.current_level + 0.1)
        # Respons pendek dan topik berganti mungkin menunjukkan kurangnya minat
        elif user_response_length < 20 and not topic_continued:
            self.current_level = max(0.3, self.current_level - 0.1)  # Jangan turun terlalu rendah
