#!/usr/bin/env python3
# event_triggers.py - Implementasi pemicu emosi berdasarkan peristiwa untuk LACIA AI

from typing import Dict, List, Any, Callable
import json
import os
import time

class EventTriggers:
    """
    Kelas yang mengatur dan memproses pemicu emosi berdasarkan peristiwa sistem
    atau interaksi eksternal pada LACIA AI.
    """
    
    def __init__(self, triggers_config_path: str = None):
        """
        Inisialisasi sistem pemicu peristiwa
        
        Args:
            triggers_config_path: Path ke file konfigurasi pemicu
        """
        self.triggers = self._load_triggers_config(triggers_config_path)
        self.event_history = []
        self.active_emotional_states = {}
        self.max_history_length = 20
        self.callbacks = {}  # Fungsi callback untuk jenis peristiwa
        
    def _load_triggers_config(self, config_path: str = None) -> Dict[str, Any]:
        """
        Memuat konfigurasi pemicu dari file atau menggunakan konfigurasi default
        
        Args:
            config_path: Path ke file konfigurasi
            
        Returns:
            Konfigurasi pemicu peristiwa berupa dictionary
        """
        default_config = {
            "user_greeting": {
                "emotions": {"senang": 0.3, "terkejut": 0.1},
                "decay_rate": 0.05,  # Kecepatan berkurangnya respons emosional
                "threshold": 0.2     # Ambang batas untuk mengaktifkan respons
            },
            "user_farewell": {
                "emotions": {"netral": 0.5},
                "decay_rate": 0.1,
                "threshold": 0.1
            },
            "user_compliment": {
                "emotions": {"senang": 0.5, "terkejut": 0.2},
                "decay_rate": 0.02,
                "threshold": 0.1
            },
            "user_criticism": {
                "emotions": {"sedih": 0.3, "bingung": 0.2},
                "decay_rate": 0.05,
                "threshold": 0.3
            },
            "error_occurred": {
                "emotions": {"bingung": 0.4, "sedih": 0.2},
                "decay_rate": 0.1,
                "threshold": 0.2
            },
            "task_completed": {
                "emotions": {"senang": 0.4},
                "decay_rate": 0.05,
                "threshold": 0.1
            },
            "system_startup": {
                "emotions": {"terkejut": 0.3, "senang": 0.2},
                "decay_rate": 0.2,
                "threshold": 0.1
            },
            "system_shutdown": {
                "emotions": {"sedih": 0.3},
                "decay_rate": 0.1,
                "threshold": 0.1
            },
            "new_skill_learned": {
                "emotions": {"senang": 0.5, "terkejut": 0.3},
                "decay_rate": 0.01,
                "threshold": 0.1
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading event triggers config: {e}")
                return default_config
        else:
            return default_config
    
    def register_callback(self, event_type: str, callback: Callable) -> None:
        """
        Mendaftarkan fungsi callback untuk jenis peristiwa tertentu
        
        Args:
            event_type: Jenis peristiwa
            callback: Fungsi yang akan dipanggil saat peristiwa terjadi
        """
        self.callbacks[event_type] = callback
        
    def trigger_event(self, event_type: str, intensity: float = 1.0, 
                      additional_data: Dict[str, Any] = None) -> Dict[str, float]:
        """
        Memicu peristiwa dan menghasilkan respons emosional
        
        Args:
            event_type: Jenis peristiwa
            intensity: Intensitas peristiwa (0-1)
            additional_data: Data tambahan peristiwa
            
        Returns:
            Dictionary respons emosional
        """
        if event_type not in self.triggers:
            return {}
            
        # Dapatkan konfigurasi pemicu
        trigger_config = self.triggers[event_type]
        threshold = trigger_config.get("threshold", 0.1)
        
        # Periksa apakah intensitas melebihi ambang batas
        if intensity < threshold:
            return {}
            
        # Dapatkan respons emosional
        emotions = trigger_config.get("emotions", {})
        
        # Sesuaikan intensitas respons emosional
        adjusted_emotions = {}
        for emotion, base_value in emotions.items():
            adjusted_value = base_value * intensity
            adjusted_emotions[emotion] = min(1.0, adjusted_value)  # Pastikan tidak melebihi 1.0
            
            # Perbarui keadaan emosional aktif
            if emotion in self.active_emotional_states:
                # Kombinasikan dengan keadaan yang ada
                current_value = self.active_emotional_states[emotion]
                self.active_emotional_states[emotion] = max(current_value, adjusted_value)
            else:
                self.active_emotional_states[emotion] = adjusted_value
        
        # Catat peristiwa ke dalam riwayat
        timestamp = time.time()
        event_record = {
            "event_type": event_type,
            "timestamp": timestamp,
            "intensity": intensity,
            "emotions": adjusted_emotions,
            "additional_data": additional_data or {}
        }
        self.event_history.append(event_record)
        
        # Batasi ukuran riwayat
        if len(self.event_history) > self.max_history_length:
            self.event_history.pop(0)
            
        # Panggil fungsi callback jika ada
        if event_type in self.callbacks:
            try:
                self.callbacks[event_type](adjusted_emotions, additional_data)
            except Exception as e:
                print(f"Error in event callback for {event_type}: {e}")
                
        return adjusted_emotions
        
    def decay_emotional_states(self) -> None:
        """
        Mengurangi intensitas keadaan emosional aktif seiring waktu
        """
        emotions_to_remove = []
        
        for emotion, value in self.active_emotional_states.items():
            # Temukan semua pemicu terkait dengan emosi ini
            decay_rates = []
            for trigger_config in self.triggers.values():
                if emotion in trigger_config.get("emotions", {}):
                    decay_rates.append(trigger_config.get("decay_rate", 0.05))
            
            # Gunakan tingkat penurunan rata-rata atau default
            avg_decay_rate = sum(decay_rates) / len(decay_rates) if decay_rates else 0.05
            
            # Kurangi nilai
            new_value = value - avg_decay_rate
            
            if new_value <= 0:
                emotions_to_remove.append(emotion)
            else:
                self.active_emotional_states[emotion] = new_value
                
        # Hapus emosi yang sudah memudar
        for emotion in emotions_to_remove:
            del self.active_emotional_states[emotion]
            
    def get_active_emotional_state(self) -> Dict[str, float]:
        """
        Mendapatkan keadaan emosional aktif saat ini
        
        Returns:
            Dictionary berisi emosi aktif dan intensitasnya
        """
        return self.active_emotional_states.copy()
    
    def get_dominant_emotion(self) -> str:
        """
        Mendapatkan emosi dominan saat ini
        
        Returns:
            Nama emosi dominan atau "netral" jika tidak ada
        """
        if not self.active_emotional_states:
            return "netral"
            
        return max(self.active_emotional_states.items(), key=lambda x: x[1])[0]
    
    def get_recent_events(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        Mendapatkan peristiwa terbaru dari riwayat
        
        Args:
            count: Jumlah peristiwa yang akan diambil
            
        Returns:
            Daftar peristiwa terbaru
        """
        return self.event_history[-count:] if self.event_history else []
    
    def get_event_pattern(self, event_type: str, time_window: float = 300) -> List[Dict[str, Any]]:
        """
        Mendapatkan pola peristiwa tertentu dalam jendela waktu tertentu
        
        Args:
            event_type: Jenis peristiwa yang dicari
            time_window: Jendela waktu dalam detik
            
        Returns:
            Daftar peristiwa yang sesuai
        """
        current_time = time.time()
        cutoff_time = current_time - time_window
        
        matching_events = []
        for event in self.event_history:
            if event["event_type"] == event_type and event["timestamp"] >= cutoff_time:
                matching_events.append(event)
                
        return matching_events
    
    def save_event_history(self, file_path: str) -> bool:
        """
        Menyimpan riwayat peristiwa ke file
        
        Args:
            file_path: Path ke file tujuan
            
        Returns:
            True jika berhasil, False jika gagal
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.event_history, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving event history: {e}")
            return False
    
    def load_event_history(self, file_path: str) -> bool:
        """
        Memuat riwayat peristiwa dari file
        
        Args:
            file_path: Path ke file sumber
            
        Returns:
            True jika berhasil, False jika gagal
        """
        if not os.path.exists(file_path):
            return False
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.event_history = json.load(f)
            return True
        except Exception as e:
            print(f"Error loading event history: {e}")
            return False