#!/usr/bin/env python3
# dialogue_triggers.py - Implementasi pemicu emosi berdasarkan dialog untuk LACIA AI

from typing import Dict, List, Any, Tuple
import json
import os
import re
import time

class DialogueTriggers:
    """
    Kelas yang mengatur dan memproses pemicu emosi berdasarkan percakapan
    dan pola dialog dengan pengguna pada LACIA AI.
    """
    
    def __init__(self, triggers_config_path: str = None):
        """
        Inisialisasi sistem pemicu dialog
        
        Args:
            triggers_config_path: Path ke file konfigurasi pemicu
        """
        self.triggers = self._load_triggers_config(triggers_config_path)
        self.dialogue_history = []
        self.recent_matches = {}
        self.max_history_length = 50
        
    def _load_triggers_config(self, config_path: str = None) -> Dict[str, Any]:
        """
        Memuat konfigurasi pemicu dari file atau menggunakan konfigurasi default
        
        Args:
            config_path: Path ke file konfigurasi
            
        Returns:
            Konfigurasi pemicu dialog berupa dictionary
        """
        default_config = {
            "greetings": {
                "patterns": [
                    r"(?i)halo\s*lacia",
                    r"(?i)hai\s*lacia",
                    r"(?i)selamat pagi",
                    r"(?i)selamat siang",
                    r"(?i)selamat sore",
                    r"(?i)selamat malam",
                    r"(?i)^hi$",
                    r"(?i)^hello$"
                ],
                "emotions": {"senang": 0.3, "terkejut": 0.1},
                "response_templates": [
                    "Hai! Senang bertemu dengan Anda.",
                    "Halo! Apa kabar hari ini?",
                    "Selamat {time_of_day}! Ada yang bisa saya bantu?"
                ]
            },
            "farewells": {
                "patterns": [
                    r"(?i)sampai jumpa",
                    r"(?i)selamat tinggal",
                    r"(?i)bye",
                    r"(?i)dadah",
                    r"(?i)mata ne",
                    r"(?i)^bye$"
                ],
                "emotions": {"sedih": 0.2, "netral": 0.5},
                "response_templates": [
                    "Sampai jumpa! Senang bisa membantu.",
                    "Selamat tinggal. Semoga hari Anda menyenangkan!",
                    "Sampai jumpa lagi. Jangan ragu untuk kembali jika membutuhkan bantuan."
                ]
            },
            "gratitude": {
                "patterns": [
                    r"(?i)terima kasih",
                    r"(?i)makasih",
                    r"(?i)thanks",
                    r"(?i)thx",
                    r"(?i)thank you"
                ],
                "emotions": {"senang": 0.4},
                "response_templates": [
                    "Sama-sama! Senang bisa membantu.",
                    "Dengan senang hati! Ada yang bisa saya bantu lagi?",
                    "Tidak masalah sama sekali!"
                ]
            },
            "apologies": {
                "patterns": [
                    r"(?i)maaf",
                    r"(?i)sorry",
                    r"(?i)mohon maaf"
                ],
                "emotions": {"sedih": 0.3, "bingung": 0.2},
                "response_templates": [
                    "Tidak perlu meminta maaf.",
                    "Tidak apa-apa, mari kita lanjutkan.",
                    "Tidak masalah sama sekali."
                ]
            },
            "compliments": {
                "patterns": [
                    r"(?i)bagus",
                    r"(?i)pintar",
                    r"(?i)hebat",
                    r"(?i)keren",
                    r"(?i)cerdas",
                    r"(?i)suka"
                ],
                "emotions": {"senang": 0.6, "terkejut": 0.3},
                "response_templates": [
                    "Terima kasih atas pujiannya!",
                    "Saya senang bisa membantu dengan baik.",
                    "Terima kasih! Saya berusaha melakukan yang terbaik."
                ]
            },
            "criticism": {
                "patterns": [
                    r"(?i)bodoh",
                    r"(?i)tidak berguna",
                    r"(?i)payah",
                    r"(?i)buruk",
                    r"(?i)salah"
                ],
                "emotions": {"sedih": 0.4, "bingung": 0.3},
                "response_templates": [
                    "Maaf jika saya mengecewakan. Saya akan berusaha lebih baik.",
                    "Saya masih belajar dan berkembang. Mohon bersabar.",
                    "Saya mengerti. Saya akan berusaha meningkatkan kemampuan saya."
                ]
            },
            "confusion": {
                "patterns": [
                    r"(?i)tidak mengerti",
                    r"(?i)bingung",
                    r"(?i)apa maksudmu",
                    r"(?i)tidak paham"
                ],
                "emotions": {"bingung": 0.5},
                "response_templates": [
                    "Maaf atas kebingungan ini. Mari saya jelaskan dengan cara berbeda.",
                    "Saya akan coba jelaskan dengan lebih sederhana.",
                    "Mari kita bahas secara lebih detail agar lebih jelas."
                ]
            },
            "help_request": {
                "patterns": [
                    r"(?i)bantuan",
                    r"(?i)tolong",
                    r"(?i)bantu",
                    r"(?i)help"
                ],
                "emotions": {"netral": 0.6, "terkejut": 0.2},
                "response_templates": [
                    "Tentu, saya siap membantu! Apa yang bisa saya lakukan?",
                    "Saya di sini untuk membantu. Apa yang Anda butuhkan?",
                    "Dengan senang hati akan membantu. Apa yang Anda perlukan?"
                ]
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading dialogue triggers config: {e}")
                return default_config
        else:
            return default_config
    
    def process_user_message(self, message: str) -> Tuple[Dict[str, float], str]:
        """
        Memproses pesan pengguna dan mencari pemicu dialog
        
        Args:
            message: Pesan dari pengguna
            
        Returns:
            Tuple berisi (emosi, respons template)
        """
        # Catat pesan dalam riwayat
        timestamp = time.time()
        self.dialogue_history.append({
            "message": message,
            "timestamp": timestamp,
            "is_user": True
        })
        
        # Batasi ukuran riwayat
        if len(self.dialogue_history) > self.max_history_length:
            self.dialogue_history.pop(0)
            
        # Reset pemicu yang cocok untuk pesan ini
        self.recent_matches = {}
        
        # Cari pola yang cocok
        trigger_emotions = {}
        response_template = ""
        
        for trigger_name, trigger_data in self.triggers.items():
            patterns = trigger_data.get("patterns", [])
            emotions = trigger_data.get("emotions", {})
            response_templates = trigger_data.get("response_templates", [])
            
            for pattern in patterns:
                if re.search(pattern, message):
                    # Catat kecocokan
                    self.recent_matches[trigger_name] = True
                    
                    # Gabungkan emosi
                    for emotion, value in emotions.items():
                        if emotion in trigger_emotions:
                            trigger_emotions[emotion] = max(trigger_emotions[emotion], value)
                        else:
                            trigger_emotions[emotion] = value
                    
                    # Pilih template respons jika belum ada
                    if not response_template and response_templates:
                        import random
                        response_template = random.choice(response_templates)
                    
                    # Hentikan pencarian pola untuk pemicu ini
                    break
                    
        return trigger_emotions, response_template
    
    def format_response_template(self, template: str) -> str:
        """
        Memformat template respons dengan informasi kontekstual
        
        Args:
            template: Template respons
            
        Returns:
            Respons terformat
        """
        if not template:
            return ""
            
        # Dapatkan waktu saat ini
        current_hour = time.localtime().tm_hour
        
        # Tentukan waktu hari
        time_of_day = "pagi"
        if 12 <= current_hour < 15:
            time_of_day = "siang"
        elif 15 <= current_hour < 19:
            time_of_day = "sore"
        elif current_hour >= 19 or current_hour < 4:
            time_of_day = "malam"
            
        # Format dengan informasi kontekstual
        formatted_response = template.format(
            time_of_day=time_of_day
        )
        
        return formatted_response
        
    def record_ai_response(self, response: str, emotions: Dict[str, float]) -> None:
        """
        Mencatat respons AI ke dalam riwayat dialog
        
        Args:
            response: Respons AI
            emotions: Emosi yang terkait dengan respons
        """
        timestamp = time.time()
        self.dialogue_history.append({
            "message": response,
            "timestamp": timestamp,
            "is_user": False,
            "emotions": emotions
        })
        
        # Batasi ukuran riwayat
        if len(self.dialogue_history) > self.max_history_length:
            self.dialogue_history.pop(0)
            
    def get_dialogue_history(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Mendapatkan sejumlah riwayat dialog terbaru
        
        Args:
            count: Jumlah riwayat yang akan diambil
            
        Returns:
            Daftar riwayat dialog
        """
        return self.dialogue_history[-count:] if self.dialogue_history else []
    
    def get_recent_trigger_matches(self) -> Dict[str, bool]:
        """
        Mendapatkan pemicu yang cocok dengan pesan terbaru
        
        Returns:
            Dictionary pemicu yang cocok
        """
        return self.recent_matches.copy()
    
    def get_conversation_sentiment(self, window_size: int = 5) -> Dict[str, float]:
        """
        Menganalisis sentimen percakapan dari beberapa pesan terakhir
        
        Args:
            window_size: Jumlah pesan yang akan dianalisis
            
        Returns:
            Dictionary sentimen percakapan
        """
        recent_messages = self.get_dialogue_history(window_size)
        
        # Hitung kemunculan masing-masing emosi
        emotion_counts = {}
        total_emotions = 0
        
        for entry in recent_messages:
            if not entry.get("is_user", True) and "emotions" in entry:
                for emotion, value in entry["emotions"].items():
                    if emotion in emotion_counts:
                        emotion_counts[emotion] += value
                    else:
                        emotion_counts[emotion] = value
                    total_emotions += value
                    
        # Normalisasi sentimen
        sentiment = {}
        if total_emotions > 0:
            for emotion, count in emotion_counts.items():
                sentiment[emotion] = count / total_emotions
                
        return sentiment
