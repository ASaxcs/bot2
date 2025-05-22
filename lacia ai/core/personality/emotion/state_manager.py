#!/usr/bin/env python3
# state_manager.py - Sistem manajemen state emosi untuk LACIA AI

import json
import os
import time
import random
from typing import Dict, List, Any, Tuple, Optional
from enum import Enum
from dataclasses import dataclass
import math

class EmotionType(Enum):
    """Enum untuk tipe-tipe emosi dasar"""
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    NEUTRAL = "neutral"
    EXCITED = "excited"
    CALM = "calm"
    CONFUSED = "confused"
    CURIOUS = "curious"
    EMPATHETIC = "empathetic"

class MoodType(Enum):
    """Enum untuk tipe-tipe mood/suasana hati"""
    CHEERFUL = "cheerful"
    MELANCHOLIC = "melancholic"
    IRRITABLE = "irritable"
    ANXIOUS = "anxious"
    SERENE = "serene"
    ENTHUSIASTIC = "enthusiastic"
    CONTEMPLATIVE = "contemplative"
    PLAYFUL = "playful"
    SERIOUS = "serious"
    SUPPORTIVE = "supportive"

@dataclass
class EmotionState:
    """Kelas data untuk menyimpan state emosi"""
    emotion_type: EmotionType
    intensity: float  # 0.0 - 1.0
    duration: float   # dalam detik
    timestamp: float
    trigger_source: str = ""
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}

@dataclass
class MoodState:
    """Kelas data untuk menyimpan state mood"""
    mood_type: MoodType
    stability: float  # 0.0 - 1.0, seberapa stabil mood ini
    influence: float  # 0.0 - 1.0, seberapa kuat pengaruh mood
    timestamp: float
    contributing_emotions: List[EmotionType] = None
    
    def __post_init__(self):
        if self.contributing_emotions is None:
            self.contributing_emotions = []

class EmotionStateManager:
    """
    Kelas untuk mengelola state emosi dan mood LACIA AI
    """
    
    def __init__(self, config_path: str = None, mood_matrix_path: str = None):
        """
        Inisialisasi emotion state manager
        
        Args:
            config_path: Path ke file konfigurasi
            mood_matrix_path: Path ke file mood matrix
        """
        self.config = self._load_config(config_path)
        self.mood_matrix = self._load_mood_matrix(mood_matrix_path)
        
        # State emosi saat ini
        self.current_emotions: List[EmotionState] = []
        self.current_mood: MoodState = MoodState(
            mood_type=MoodType.SERENE,
            stability=0.8,
            influence=0.5,
            timestamp=time.time()
        )
        
        # Riwayat emosi dan mood
        self.emotion_history: List[EmotionState] = []
        self.mood_history: List[MoodState] = []
        
        # Pengaturan sistem
        self.max_concurrent_emotions = self.config.get("max_concurrent_emotions", 3)
        self.emotion_decay_rate = self.config.get("emotion_decay_rate", 0.1)
        self.mood_transition_threshold = self.config.get("mood_transition_threshold", 0.6)
        self.max_history_length = self.config.get("max_history_length", 100)
        
        # Variabel untuk tracking
        self.last_update_time = time.time()
        self.emotion_triggers_active = True
        self.mood_adaptation_active = True
        
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """Memuat konfigurasi sistem emosi"""
        default_config = {
            "max_concurrent_emotions": 3,
            "emotion_decay_rate": 0.1,
            "mood_transition_threshold": 0.6,
            "max_history_length": 100,
            "emotion_intensity_range": [0.1, 1.0],
            "mood_stability_factor": 0.8,
            "emotion_blending_enabled": True,
            "contextual_adaptation": True,
            "personality_influence": {
                "openness": 0.7,
                "conscientiousness": 0.6,
                "extraversion": 0.8,
                "agreeableness": 0.9,
                "neuroticism": 0.3
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except Exception as e:
                print(f"Error loading emotion config: {e}")
                
        return default_config
    
    def _load_mood_matrix(self, matrix_path: str = None) -> Dict[str, Any]:
        """Memuat matriks transisi mood"""
        default_matrix = {
            "emotion_to_mood_mapping": {
                "happy": ["cheerful", "enthusiastic", "playful"],
                "sad": ["melancholic", "contemplative", "serious"],
                "angry": ["irritable", "serious"],
                "fear": ["anxious", "serious"],
                "surprise": ["enthusiastic", "curious"],
                "disgust": ["irritable", "serious"],
                "neutral": ["serene", "contemplative"],
                "excited": ["enthusiastic", "playful"],
                "calm": ["serene", "contemplative"],
                "confused": ["contemplative", "curious"],
                "curious": ["contemplative", "enthusiastic"],
                "empathetic": ["supportive", "serene"]
            },
            "mood_transitions": {
                "cheerful": {
                    "melancholic": 0.1,
                    "irritable": 0.2,
                    "anxious": 0.1,
                    "serene": 0.3,
                    "enthusiastic": 0.8,
                    "contemplative": 0.2,
                    "playful": 0.9,
                    "serious": 0.1,
                    "supportive": 0.6
                },
                "melancholic": {
                    "cheerful": 0.2,
                    "irritable": 0.3,
                    "anxious": 0.4,
                    "serene": 0.5,
                    "enthusiastic": 0.1,
                    "contemplative": 0.8,
                    "playful": 0.1,
                    "serious": 0.7,
                    "supportive": 0.4
                },
                # ... (tambahkan transisi lainnya sesuai kebutuhan)
            },
            "emotion_combinations": {
                ("happy", "excited"): {"resulting_mood": "enthusiastic", "intensity_multiplier": 1.3},
                ("sad", "angry"): {"resulting_mood": "irritable", "intensity_multiplier": 1.1},
                ("curious", "happy"): {"resulting_mood": "playful", "intensity_multiplier": 1.2},
                # ... (tambahkan kombinasi lainnya)
            }
        }
        
        if matrix_path and os.path.exists(matrix_path):
            try:
                with open(matrix_path, 'r', encoding='utf-8') as f:
                    loaded_matrix = json.load(f)
                    default_matrix.update(loaded_matrix)
            except Exception as e:
                print(f"Error loading mood matrix: {e}")
                
        return default_matrix
    
    def add_emotion(self, emotion_type: EmotionType, intensity: float, 
                   duration: float = 60.0, trigger_source: str = "", 
                   context: Dict[str, Any] = None) -> None:
        """
        Menambahkan emosi baru ke state saat ini
        
        Args:
            emotion_type: Tipe emosi
            intensity: Intensitas emosi (0.0 - 1.0)
            duration: Durasi emosi dalam detik
            trigger_source: Sumber pemicu emosi
            context: Konteks tambahan
        """
        # Validasi intensity
        min_intensity, max_intensity = self.config.get("emotion_intensity_range", [0.1, 1.0])
        intensity = max(min_intensity, min(max_intensity, intensity))
        
        # Buat state emosi baru
        new_emotion = EmotionState(
            emotion_type=emotion_type,
            intensity=intensity,
            duration=duration,
            timestamp=time.time(),
            trigger_source=trigger_source,
            context=context or {}
        )
        
        # Cek apakah emosi serupa sudah ada
        existing_emotion = self._find_existing_emotion(emotion_type)
        
        if existing_emotion:
            # Gabungkan dengan emosi yang sudah ada
            self._blend_emotions(existing_emotion, new_emotion)
        else:
            # Tambahkan emosi baru
            self.current_emotions.append(new_emotion)
            
        # Batasi jumlah emosi concurrent
        self._limit_concurrent_emotions()
        
        # Tambahkan ke riwayat
        self.emotion_history.append(new_emotion)
        self._limit_history_length()
        
        # Update mood berdasarkan emosi baru
        self._update_mood_from_emotions()
        
    def _find_existing_emotion(self, emotion_type: EmotionType) -> Optional[EmotionState]:
        """Mencari emosi yang sudah ada dengan tipe yang sama"""
        for emotion in self.current_emotions:
            if emotion.emotion_type == emotion_type:
                return emotion
        return None
    
    def _blend_emotions(self, existing: EmotionState, new: EmotionState) -> None:
        """Menggabungkan emosi yang sudah ada dengan emosi baru"""
        if self.config.get("emotion_blending_enabled", True):
            # Gabungkan intensitas (weighted average)
            total_weight = existing.intensity + new.intensity
            existing.intensity = (existing.intensity * existing.intensity + 
                                new.intensity * new.intensity) / total_weight
            
            # Update durasi (ambil yang lebih lama)
            existing.duration = max(existing.duration, new.duration)
            
            # Update timestamp
            existing.timestamp = time.time()
            
            # Gabungkan konteks
            existing.context.update(new.context)
            
            # Update trigger source jika lebih spesifik
            if new.trigger_source and len(new.trigger_source) > len(existing.trigger_source):
                existing.trigger_source = new.trigger_source
    
    def _limit_concurrent_emotions(self) -> None:
        """Membatasi jumlah emosi yang berjalan bersamaan"""
        if len(self.current_emotions) > self.max_concurrent_emotions:
            # Urutkan berdasarkan intensitas dan timestamp
            self.current_emotions.sort(
                key=lambda e: (e.intensity, e.timestamp), 
                reverse=True
            )
            # Hapus emosi dengan intensitas terendah
            self.current_emotions = self.current_emotions[:self.max_concurrent_emotions]
    
    def _limit_history_length(self) -> None:
        """Membatasi panjang riwayat emosi dan mood"""
        if len(self.emotion_history) > self.max_history_length:
            self.emotion_history = self.emotion_history[-self.max_history_length:]
            
        if len(self.mood_history) > self.max_history_length:
            self.mood_history = self.mood_history[-self.max_history_length:]
    
    def update_emotions(self) -> None:
        """Memperbarui state emosi (decay, expiration, dll.)"""
        current_time = time.time()
        time_delta = current_time - self.last_update_time
        
        # Update setiap emosi
        emotions_to_remove = []
        
        for emotion in self.current_emotions:
            # Hitung decay
            age = current_time - emotion.timestamp
            
            # Cek apakah emosi sudah expired
            if age >= emotion.duration:
                emotions_to_remove.append(emotion)
                continue
                
            # Terapkan decay pada intensitas
            decay_factor = 1.0 - (self.emotion_decay_rate * time_delta)
            emotion.intensity *= decay_factor
            
            # Hapus emosi dengan intensitas sangat rendah
            if emotion.intensity < 0.05:
                emotions_to_remove.append(emotion)
        
        # Hapus emosi yang expired atau terlalu lemah
        for emotion in emotions_to_remove:
            self.current_emotions.remove(emotion)
            
        self.last_update_time = current_time
        
        # Update mood jika ada perubahan emosi
        if emotions_to_remove:
            self._update_mood_from_emotions()
    
    def _update_mood_from_emotions(self) -> None:
        """Memperbarui mood berdasarkan emosi saat ini"""
        if not self.mood_adaptation_active:
            return
            
        if not self.current_emotions:
            # Tidak ada emosi, kembalikan ke mood netral
            self._transition_to_mood(MoodType.SERENE, 0.8, 0.5)
            return
            
        # Hitung mood berdasarkan emosi dominan
        emotion_weights = {}
        
        for emotion in self.current_emotions:
            emotion_name = emotion.emotion_type.value
            if emotion_name not in emotion_weights:
                emotion_weights[emotion_name] = 0
            emotion_weights[emotion_name] += emotion.intensity
            
        # Cari emosi dominan
        dominant_emotion = max(emotion_weights.items(), key=lambda x: x[1])
        dominant_emotion_name = dominant_emotion[0]
        dominant_intensity = dominant_emotion[1]
        
        # Dapatkan mood yang sesuai dari matriks
        possible_moods = self.mood_matrix.get("emotion_to_mood_mapping", {}).get(
            dominant_emotion_name, ["serene"]
        )
        
        # Pilih mood berdasarkan konteks dan kombinasi emosi
        selected_mood = self._select_appropriate_mood(possible_moods, emotion_weights)
        
        # Cek apakah perlu transisi mood
        if (selected_mood != self.current_mood.mood_type and 
            dominant_intensity > self.mood_transition_threshold):
            
            # Hitung parameter mood baru
            stability = self._calculate_mood_stability(emotion_weights)
            influence = min(1.0, dominant_intensity * 1.2)
            
            self._transition_to_mood(selected_mood, stability, influence)
    
    def _select_appropriate_mood(self, possible_moods: List[str], 
                               emotion_weights: Dict[str, float]) -> MoodType:
        """Memilih mood yang paling sesuai dari daftar kemungkinan"""
        if not possible_moods:
            return MoodType.SERENE
            
        # Jika hanya satu pilihan
        if len(possible_moods) == 1:
            return MoodType(possible_moods[0])
            
        # Analisis kombinasi emosi untuk mood yang lebih spesifik
        emotion_combinations = self.mood_matrix.get("emotion_combinations", {})
        
        for combination, result in emotion_combinations.items():
            if all(emotion in emotion_weights for emotion in combination):
                # Cek apakah kombinasi emosi cukup kuat
                combined_intensity = sum(emotion_weights[emotion] for emotion in combination)
                if combined_intensity > 0.8:
                    resulting_mood = result.get("resulting_mood")
                    if resulting_mood in possible_moods:
                        return MoodType(resulting_mood)
        
        # Default: pilih mood pertama dari daftar
        return MoodType(possible_moods[0])
    
    def _calculate_mood_stability(self, emotion_weights: Dict[str, float]) -> float:
        """Menghitung stabilitas mood berdasarkan distribusi emosi"""
        if not emotion_weights:
            return 0.8
            
        # Hitung entropy dari distribusi emosi
        total_weight = sum(emotion_weights.values())
        if total_weight == 0:
            return 0.8
            
        entropy = 0
        for weight in emotion_weights.values():
            if weight > 0:
                p = weight / total_weight
                entropy -= p * math.log2(p)
                
        # Normalisasi entropy ke rentang 0-1
        max_entropy = math.log2(len(emotion_weights)) if len(emotion_weights) > 1 else 1
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        # Stabilitas tinggi jika entropy rendah (emosi terfokus)
        stability = 1.0 - normalized_entropy
        
        # Terapkan faktor stabilitas dari konfigurasi
        stability *= self.config.get("mood_stability_factor", 0.8)
        
        return max(0.1, min(1.0, stability))
    
    def _transition_to_mood(self, new_mood: MoodType, stability: float, 
                          influence: float) -> None:
        """Melakukan transisi ke mood baru"""
        # Simpan mood lama ke riwayat
        self.mood_history.append(self.current_mood)
        
        # Buat mood baru
        contributing_emotions = [emotion.emotion_type for emotion in self.current_emotions]
        
        self.current_mood = MoodState(
            mood_type=new_mood,
            stability=stability,
            influence=influence,
            timestamp=time.time(),
            contributing_emotions=contributing_emotions
        )
    
    def get_current_emotional_state(self) -> Dict[str, Any]:
        """Mendapatkan state emosi saat ini"""
        return {
            "emotions": [
                {
                    "type": emotion.emotion_type.value,
                    "intensity": emotion.intensity,
                    "duration_remaining": max(0, emotion.duration - (time.time() - emotion.timestamp)),
                    "trigger_source": emotion.trigger_source,
                    "context": emotion.context
                }
                for emotion in self.current_emotions
            ],
            "mood": {
                "type": self.current_mood.mood_type.value,
                "stability": self.current_mood.stability,
                "influence": self.current_mood.influence,
                "age": time.time() - self.current_mood.timestamp,
                "contributing_emotions": [e.value for e in self.current_mood.contributing_emotions]
            },
            "dominant_emotion": self._get_dominant_emotion(),
            "emotional_intensity": self._calculate_overall_intensity(),
            "last_update": self.last_update_time
        }
    
    def _get_dominant_emotion(self) -> Optional[str]:
        """Mendapatkan emosi dominan saat ini"""
        if not self.current_emotions:
            return None
            
        dominant = max(self.current_emotions, key=lambda e: e.intensity)
        return dominant.emotion_type.value
    
    def _calculate_overall_intensity(self) -> float:
        """Menghitung intensitas emosi keseluruhan"""
        if not self.current_emotions:
            return 0.0
            
        # Hitung weighted average dari semua emosi
        total_intensity = sum(emotion.intensity for emotion in self.current_emotions)
        return min(1.0, total_intensity / len(self.current_emotions))
    
    def get_emotion_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Mendapatkan riwayat emosi"""
        recent_emotions = self.emotion_history[-limit:] if limit > 0 else self.emotion_history
        
        return [
            {
                "type": emotion.emotion_type.value,
                "intensity": emotion.intensity,
                "timestamp": emotion.timestamp,
                "trigger_source": emotion.trigger_source,
                "context": emotion.context
            }
            for emotion in recent_emotions
        ]
    
    def get_mood_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Mendapatkan riwayat mood"""
        recent_moods = self.mood_history[-limit:] if limit > 0 else self.mood_history
        
        return [
            {
                "type": mood.mood_type.value,
                "stability": mood.stability,
                "influence": mood.influence,
                "timestamp": mood.timestamp,
                "contributing_emotions": [e.value for e in mood.contributing_emotions]
            }
            for mood in recent_moods
        ]
    
    def force_emotion(self, emotion_type: EmotionType, intensity: float, 
                     duration: float = 30.0) -> None:
        """Memaksa emosi tertentu (untuk testing atau situasi khusus)"""
        self.add_emotion(
            emotion_type=emotion_type,
            intensity=intensity,
            duration=duration,
            trigger_source="forced",
            context={"forced": True}
        )
    
    def clear_emotions(self) -> None:
        """Menghapus semua emosi saat ini"""
        self.current_emotions.clear()
        self._transition_to_mood(MoodType.SERENE, 0.8, 0.5)
    
    def set_emotion_sensitivity(self, sensitivity: float) -> None:
        """Mengatur sensitivitas sistem emosi"""
        self.emotion_decay_rate = max(0.01, min(1.0, sensitivity))
        self.mood_transition_threshold = max(0.1, min(1.0, 1.0 - sensitivity))
    
    def get_emotional_context_for_response(self) -> Dict[str, Any]:
        """Mendapatkan konteks emosi untuk generation respons"""
        state = self.get_current_emotional_state()
        
        return {
            "should_adapt_tone": len(self.current_emotions) > 0,
            "dominant_emotion": state["dominant_emotion"],
            "current_mood": state["mood"]["type"],
            "emotional_intensity": state["emotional_intensity"],
            "mood_stability": state["mood"]["stability"],
            "suggested_response_tone": self._suggest_response_tone(),
            "emotional_keywords": self._get_emotional_keywords()
        }
    
    def _suggest_response_tone(self) -> str:
        """Menyarankan tone respons berdasarkan mood saat ini"""
        mood_to_tone = {
            MoodType.CHEERFUL: "upbeat",
            MoodType.MELANCHOLIC: "gentle",
            MoodType.IRRITABLE: "calm",
            MoodType.ANXIOUS: "reassuring",
            MoodType.SERENE: "balanced",
            MoodType.ENTHUSIASTIC: "energetic",
            MoodType.CONTEMPLATIVE: "thoughtful",
            MoodType.PLAYFUL: "lighthearted",
            MoodType.SERIOUS: "formal",
            MoodType.SUPPORTIVE: "empathetic"
        }
        
        return mood_to_tone.get(self.current_mood.mood_type, "balanced")
    
    def _get_emotional_keywords(self) -> List[str]:
        """Mendapatkan kata kunci emosional untuk respons"""
        if not self.current_emotions:
            return ["calm", "balanced"]
            
        keywords = []
        for emotion in self.current_emotions:
            emotion_keywords = {
                EmotionType.HAPPY: ["joyful", "positive", "bright"],
                EmotionType.SAD: ["gentle", "understanding", "compassionate"],
                EmotionType.ANGRY: ["calm", "measured", "patient"],
                EmotionType.FEAR: ["reassuring", "supportive", "safe"],
                EmotionType.SURPRISE: ["exciting", "unexpected", "amazing"],
                EmotionType.CURIOUS: ["interesting", "exploratory", "questioning"],
                EmotionType.EMPATHETIC: ["understanding", "caring", "supportive"]
            }
            
            keywords.extend(emotion_keywords.get(emotion.emotion_type, ["neutral"]))
            
        return list(set(keywords))  # Remove duplicates
    
    def save_state(self, filepath: str) -> bool:
        """Menyimpan state emosi ke file"""
        try:
            state_data = {
                "current_emotions": [
                    {
                        "emotion_type": emotion.emotion_type.value,
                        "intensity": emotion.intensity,
                        "duration": emotion.duration,
                        "timestamp": emotion.timestamp,
                        "trigger_source": emotion.trigger_source,
                        "context": emotion.context
                    }
                    for emotion in self.current_emotions
                ],
                "current_mood": {
                    "mood_type": self.current_mood.mood_type.value,
                    "stability": self.current_mood.stability,
                    "influence": self.current_mood.influence,
                    "timestamp": self.current_mood.timestamp,
                    "contributing_emotions": [e.value for e in self.current_mood.contributing_emotions]
                },
                "config": self.config,
                "last_update_time": self.last_update_time
            }
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)
                
            return True
        except Exception as e:
            print(f"Error saving emotion state: {e}")
            return False
    
    def load_state(self, filepath: str) -> bool:
        """Memuat state emosi dari file"""
        try:
            if not os.path.exists(filepath):
                return False
                
            with open(filepath, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
                
            # Restore emotions
            self.current_emotions = []
            for emotion_data in state_data.get("current_emotions", []):
                emotion = EmotionState(
                    emotion_type=EmotionType(emotion_data["emotion_type"]),
                    intensity=emotion_data["intensity"],
                    duration=emotion_data["duration"],
                    timestamp=emotion_data["timestamp"],
                    trigger_source=emotion_data["trigger_source"],
                    context=emotion_data["context"]
                )
                self.current_emotions.append(emotion)
                
            # Restore mood
            mood_data = state_data.get("current_mood", {})
            self.current_mood = MoodState(
                mood_type=MoodType(mood_data["mood_type"]),
                stability=mood_data["stability"],
                influence=mood_data["influence"],
                timestamp=mood_data["timestamp"],
                contributing_emotions=[EmotionType(e) for e in mood_data.get("contributing_emotions", [])]
            )
            
            # Restore config if available
            if "config" in state_data:
                self.config.update(state_data["config"])
                
            self.last_update_time = state_data.get("last_update_time", time.time())
            
            return True
        except Exception as e:
            print(f"Error loading emotion state: {e}")
            return False

# Contoh penggunaan
if __name__ == "__main__":
    # Inisialisasi emotion state manager
    emotion_manager = EmotionStateManager()
    
    # Simulasi beberapa emosi
    emotion_manager.add_emotion(EmotionType.HAPPY, 0.8, 120.0, "user_positive_feedback")
    emotion_manager.add_emotion(EmotionType.CURIOUS, 0.6, 60.0, "interesting_question")
    
    # Dapatkan state emosi saat ini
    current_state = emotion_manager.get_current_emotional_state()
    print("Current Emotional State:")
    print(f"Dominant emotion: {current_state.get('dominant_emotion')}")
    print(f"Current mood: {current_state['mood']['type']}")
    print(f"Overall intensity: {current_state['emotional_intensity']:.2f}")
    
    # Dapatkan konteks untuk respons
    response_context = emotion_manager.get_emotional_context_for_response()
    print(f"\nSuggested response tone: {response_context['suggested_response_tone']}")
    print(f"Emotional keywords: {response_context['emotional_keywords']}")
    
    # Update emosi (simulasi decay)
    time.sleep(1)
    emotion_manager.update_emotions()
    
    # Simpan state
    emotion_manager.save_state("emotion_state.json")
