#!/usr/bin/env python3
# empathy.py - Implementasi kemampuan empati LACIA AI

from typing import Dict, List, Tuple
import json
import os
import re

class Empathy:
    """
    Kelas yang mengimplementasikan kemampuan empati pada LACIA AI.
    Memungkinkan AI untuk mendeteksi emosi pengguna dan merespons dengan tepat.
    """
    
    def __init__(self, emotion_lexicon_path: str = None):
        """
        Inisialisasi sistem empati
        
        Args:
            emotion_lexicon_path: Path ke leksikon emosi
        """
        self.emotion_lexicon = self._load_emotion_lexicon(emotion_lexicon_path)
        self.last_detected_emotions = {}
        self.emotion_history = []
        self.max_history = 10  # Simpan 10 entri emosi terakhir
        
    def _load_emotion_lexicon(self, lexicon_path: str = None) -> Dict[str, Dict[str, float]]:
        """
        Memuat leksikon emosi dari file atau menggunakan leksikon default
        
        Args:
            lexicon_path: Path ke file leksikon
            
        Returns:
            Leksikon emosi berupa dictionary
        """
        default_lexicon = {
            "senang": {
                "kata": ["senang", "gembira", "bahagia", "ceria", "suka", "puas", "semangat"],
                "bobot": 1.0
            },
            "sedih": {
                "kata": ["sedih", "kecewa", "murung", "menyesal", "putus asa", "terpukul"],
                "bobot": -0.8
            },
            "marah": {
                "kata": ["marah", "kesal", "frustrasi", "jengkel", "emosi", "geram", "sebal"],
                "bobot": -0.7
            },
            "takut": {
                "kata": ["takut", "khawatir", "cemas", "gugup", "panik", "gelisah", "was-was"],
                "bobot": -0.6
            },
            "terkejut": {
                "kata": ["terkejut", "kaget", "heran", "tercengang", "terperanjat"],
                "bobot": 0.2
            },
            "bingung": {
                "kata": ["bingung", "ragu", "bimbang", "tidak yakin", "tidak mengerti"],
                "bobot": -0.3
            }
        }
        
        if lexicon_path and os.path.exists(lexicon_path):
            try:
                with open(lexicon_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading emotion lexicon: {e}")
                return default_lexicon
        else:
            return default_lexicon
    
    def detect_emotion(self, text: str) -> Dict[str, float]:
        """
        Mendeteksi emosi dari teks input
        
        Args:
            text: Teks yang akan dianalisis
            
        Returns:
            Dictionary emosi dengan nilai kepercayaan
        """
        text = text.lower()
        detected_emotions = {}
        
        # Deteksi emosi berdasarkan kata kunci
        for emotion, data in self.emotion_lexicon.items():
            score = 0.0
            keywords = data["kata"]
            weight = data["bobot"]
            
            for keyword in keywords:
                # Hitung kemunculan kata kunci dalam teks
                count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text))
                if count > 0:
                    score += count * weight
            
            if score != 0:
                detected_emotions[emotion] = min(1.0, abs(score) / 3)  # Normalisasi skor
        
        # Simpan hasil deteksi
        self.last_detected_emotions = detected_emotions
        self.emotion_history.append(detected_emotions)
        
        # Batasi ukuran history
        if len(self.emotion_history) > self.max_history:
            self.emotion_history.pop(0)
            
        return detected_emotions
    
    def get_emotional_trend(self) -> Dict[str, float]:
        """
        Mendapatkan tren emosi berdasarkan history
        
        Returns:
            Dictionary tren emosi
        """
        if not self.emotion_history:
            return {}
            
        trends = {}
        for emotion_dict in self.emotion_history:
            for emotion, value in emotion_dict.items():
                if emotion in trends:
                    trends[emotion].append(value)
                else:
                    trends[emotion] = [value]
        
        # Hitung rata-rata untuk setiap emosi
        trend_averages = {}
        for emotion, values in trends.items():
            trend_averages[emotion] = sum(values) / len(values)
            
        return trend_averages
    
    def generate_empathetic_response(self, emotion_data: Dict[str, float]) -> Tuple[str, str]:
        """
        Menghasilkan respons empatik berdasarkan emosi yang terdeteksi
        
        Args:
            emotion_data: Data emosi yang terdeteksi
            
        Returns:
            Tuple berisi (respons empati, emosi dominan)
        """
        if not emotion_data:
            return "", "netral"
            
        # Temukan emosi dominan
        dominant_emotion = max(emotion_data.items(), key=lambda x: x[1])
        emotion_name = dominant_emotion[0]
        emotion_strength = dominant_emotion[1]
        
        # Buat respons berdasarkan emosi dominan
        responses = {
            "senang": [
                "Senang mendengar Anda dalam suasana hati yang baik!",
                "Saya ikut senang melihat semangat Anda.",
                "Bagus sekali, energi positif Anda terasa!"
            ],
            "sedih": [
                "Saya mengerti ini mungkin situasi yang sulit.",
                "Saya di sini untuk mendengarkan jika Anda ingin berbagi lebih banyak.",
                "Kadang-kadang kita perlu waktu untuk memproses perasaan kita."
            ],
            "marah": [
                "Saya mengerti Anda merasa frustrasi saat ini.",
                "Terima kasih sudah membagikan perasaan Anda dengan jujur.",
                "Mari kita coba atasi masalah ini bersama dengan tenang."
            ],
            "takut": [
                "Wajar untuk merasa khawatir dalam situasi seperti ini.",
                "Mari kita bahas apa yang membuat Anda cemas.",
                "Saya di sini untuk membantu mengurangi kekhawatiran Anda."
            ],
            "terkejut": [
                "Sepertinya ini cukup mengejutkan bagi Anda.",
                "Saya mengerti ini mungkin tidak terduga.",
                "Hal-hal tak terduga memang bisa membuat kita terkejut."
            ],
            "bingung": [
                "Mari saya coba jelaskan dengan cara yang berbeda.",
                "Tidak apa-apa merasa bingung, kita bisa membahasnya perlahan.",
                "Saya akan membantu memperjelas informasi ini."
            ]
        }
        
        # Pilih respons yang sesuai dengan emosi dominan
        if emotion_name in responses:
            import random
            response = random.choice(responses[emotion_name])
        else:
            response = ""
            
        return response, emotion_name
