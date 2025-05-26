#!/usr/bin/env python3
# event_triggers.py - Sistem pemicu emosi berdasarkan event untuk LACIA AI

import time
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from state_manager import EmotionType, EmotionalStateManager

class EventType(Enum):
    """Jenis-jenis event yang dapat memicu emosi"""
    USER_PRAISE = "user_praise"
    USER_CRITICISM = "user_criticism"
    SUCCESSFUL_TASK = "successful_task"
    FAILED_TASK = "failed_task"
    NEW_LEARNING = "new_learning"
    CONFUSION_DETECTED = "confusion_detected"
    HUMOR_DETECTED = "humor_detected"
    SADNESS_DETECTED = "sadness_detected"
    ANGER_DETECTED = "anger_detected"
    EXCITEMENT_DETECTED = "excitement_detected"
    GRATITUDE_RECEIVED = "gratitude_received"
    INTERRUPTION = "interruption"
    LONG_SILENCE = "long_silence"
    RAPID_INTERACTION = "rapid_interaction"
    COMPLEX_QUESTION = "complex_question"
    SIMPLE_QUESTION = "simple_question"
    CREATIVE_REQUEST = "creative_request"
    TECHNICAL_DISCUSSION = "technical_discussion"
    PERSONAL_SHARING = "personal_sharing"
    ACHIEVEMENT_MENTIONED = "achievement_mentioned"

@dataclass
class EventTrigger:
    """Definisi pemicu emosi dari event"""
    event_type: EventType
    emotion_type: EmotionType
    intensity_base: float
    duration_base: float
    conditions: Dict[str, Any] = None
    intensity_modifiers: Dict[str, float] = None
    context_requirements: List[str] = None
    
    def __post_init__(self):
        if self.conditions is None:
            self.conditions = {}
        if self.intensity_modifiers is None:
            self.intensity_modifiers = {}
        if self.context_requirements is None:
            self.context_requirements = []

class EventEmotionTrigger:
    """
    Kelas untuk mendeteksi dan memproses event yang memicu emosi
    """
    
    def __init__(self, emotion_manager: EmotionalStateManager, config_path: str = None):
        """
        Inisialisasi event trigger system
        
        Args:
            emotion_manager: Instance dari EmotionStateManager
            config_path: Path ke file konfigurasi trigger
        """
        self.emotion_manager = emotion_manager
        self.config = self._load_config(config_path)
        self.triggers = self._initialize_triggers()
        self.event_history = []
        self.pattern_matchers = self._initialize_pattern_matchers()
        self.last_interaction_time = time.time()
        self.interaction_count = 0
        self.session_context = {}
        
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """Memuat konfigurasi trigger"""
        default_config = {
            "trigger_sensitivity": 0.7,
            "event_memory_duration": 300,  # 5 menit
            "pattern_matching_enabled": True,
            "context_awareness_enabled": True,
            "adaptive_intensity": True,
            "event_accumulation": True,
            "trigger_cooldown": {
                "user_praise": 30,
                "user_criticism": 60,
                "successful_task": 10,
                "failed_task": 30
            },
            "intensity_scaling": {
                "repetition_factor": 0.8,
                "context_bonus": 0.2,
                "time_decay": 0.1
            }
        }
        
        if config_path:
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except Exception as e:
                print(f"Error loading trigger config: {e}")
                
        return default_config
    
    def _initialize_triggers(self) -> List[EventTrigger]:
        """Inisialisasi daftar trigger default"""
        triggers = [
            # Praise dan feedback positif - Menggunakan EmotionType.JOY
            EventTrigger(
                event_type=EventType.USER_PRAISE,
                emotion_type=EmotionType.JOY,
                intensity_base=0.8,
                duration_base=120.0,
                intensity_modifiers={"repetition": 0.9, "specificity": 1.2}
            ),
            EventTrigger(
                event_type=EventType.GRATITUDE_RECEIVED,
                emotion_type=EmotionType.JOY,
                intensity_base=0.7,
                duration_base=90.0,
                intensity_modifiers={"sincerity": 1.1}
            ),
            
            # Criticism dan feedback negatif - Menggunakan EmotionType.SADNESS
            EventTrigger(
                event_type=EventType.USER_CRITICISM,
                emotion_type=EmotionType.SADNESS,
                intensity_base=0.6,
                duration_base=150.0,
                intensity_modifiers={"constructiveness": 0.8, "harshness": 1.3}
            ),
            
            # Task completion - JOY untuk sukses, SADNESS untuk gagal
            EventTrigger(
                event_type=EventType.SUCCESSFUL_TASK,
                emotion_type=EmotionType.JOY,
                intensity_base=0.6,
                duration_base=60.0,
                intensity_modifiers={"complexity": 1.2, "user_satisfaction": 1.1}
            ),
            EventTrigger(
                event_type=EventType.FAILED_TASK,
                emotion_type=EmotionType.SADNESS,
                intensity_base=0.5,
                duration_base=90.0,
                intensity_modifiers={"importance": 1.2, "effort_invested": 1.1}
            ),
            
            # Learning dan discovery - Menggunakan CURIOSITY atau JOY
            EventTrigger(
                event_type=EventType.NEW_LEARNING,
                emotion_type=EmotionType.CURIOSITY,
                intensity_base=0.7,
                duration_base=100.0,
                intensity_modifiers={"novelty": 1.3, "relevance": 1.1}
            ),
            
            # Confusion - Menggunakan CONFUSION atau NEUTRAL
            EventTrigger(
                event_type=EventType.CONFUSION_DETECTED,
                emotion_type=EmotionType.CONFUSION,
                intensity_base=0.6,
                duration_base=80.0,
                intensity_modifiers={"complexity": 1.2}
            ),
            
            # Humor dan entertainment - JOY
            EventTrigger(
                event_type=EventType.HUMOR_DETECTED,
                emotion_type=EmotionType.JOY,
                intensity_base=0.8,
                duration_base=70.0,
                intensity_modifiers={"wit_level": 1.2, "appropriateness": 1.1}
            ),
            
            # Emotional contagion - EMPATHY atau sesuai emosi yang terdeteksi
            EventTrigger(
                event_type=EventType.SADNESS_DETECTED,
                emotion_type=EmotionType.EMPATHY,
                intensity_base=0.7,
                duration_base=120.0,
                intensity_modifiers={"user_distress_level": 1.2}
            ),
            EventTrigger(
                event_type=EventType.EXCITEMENT_DETECTED,
                emotion_type=EmotionType.EXCITEMENT,
                intensity_base=0.8,
                duration_base=90.0,
                intensity_modifiers={"contagion_factor": 1.1}
            ),
            
            # Interaction patterns - EXCITEMENT atau CURIOSITY
            EventTrigger(
                event_type=EventType.RAPID_INTERACTION,
                emotion_type=EmotionType.EXCITEMENT,
                intensity_base=0.6,
                duration_base=50.0,
                intensity_modifiers={"interaction_speed": 1.2}
            ),
            EventTrigger(
                event_type=EventType.LONG_SILENCE,
                emotion_type=EmotionType.CONFUSION,
                intensity_base=0.4,
                duration_base=40.0,
                intensity_modifiers={"silence_duration": 1.1}
            ),
            
            # Question complexity - CURIOSITY
            EventTrigger(
                event_type=EventType.COMPLEX_QUESTION,
                emotion_type=EmotionType.CURIOSITY,
                intensity_base=0.7,
                duration_base=80.0,
                intensity_modifiers={"intellectual_challenge": 1.2}
            ),
            
            # Creative requests - EXCITEMENT
            EventTrigger(
                event_type=EventType.CREATIVE_REQUEST,
                emotion_type=EmotionType.EXCITEMENT,
                intensity_base=0.8,
                duration_base=100.0,
                intensity_modifiers={"creativity_scope": 1.3}
            ),
            
            # Personal connection - EMPATHY
            EventTrigger(
                event_type=EventType.PERSONAL_SHARING,
                emotion_type=EmotionType.EMPATHY,
                intensity_base=0.7,
                duration_base=150.0,
                intensity_modifiers={"intimacy_level": 1.2, "trust_indicator": 1.1}
            )
        ]
        
        return triggers
    
    def _initialize_pattern_matchers(self) -> Dict[str, List[str]]:
        """Inisialisasi pattern matcher untuk deteksi event dari teks"""
        return {
            "praise_patterns": [
                r"(?i)(excellent|amazing|fantastic|wonderful|great job|well done|perfect|brilliant|outstanding|impressive)",
                r"(?i)(thank you|thanks|appreciate|grateful|helpful)",
                r"(?i)(love (this|it|that)|this is (great|awesome|perfect))",
                r"(?i)(you('re| are) (so|very) (helpful|smart|good|amazing))"
            ],
            "criticism_patterns": [
                r"(?i)(wrong|incorrect|bad|terrible|awful|useless|stupid|dumb)",
                r"(?i)(disappointed|unsatisfied|not (good|helpful|useful))",
                r"(?i)(this (doesn't|does not) (work|help|make sense))",
                r"(?i)(you (don't|do not) understand|you('re| are) (not|no) (help|good))"
            ],
            "confusion_patterns": [
                r"(?i)(confused|don't understand|unclear|what do you mean)",
                r"(?i)(i('m| am) lost|doesn't make sense|can you explain)",
                r"(?i)(huh\?|what\?|unclear|ambiguous|vague)"
            ],
            "humor_patterns": [
                r"(?i)(haha|lol|funny|hilarious|amusing|witty)",
                r"(?i)(joke|kidding|just kidding|humor|comic)",
                r"(?i)(made me (laugh|smile)|that's funny)"
            ],
            "sadness_patterns": [
                r"(?i)(sad|depressed|down|upset|unhappy|feeling low)",
                r"(?i)(difficult time|hard time|struggling|tough)",
                r"(?i)(crying|tears|heartbroken|devastated)"
            ],
            "excitement_patterns": [
                r"(?i)(excited|thrilled|can't wait|amazing|incredible)",
                r"(?i)(wow|omg|fantastic|awesome|super)",
                r"(?i)(so (happy|excited)|this is (great|amazing))"
            ],
            "gratitude_patterns": [
                r"(?i)(thank you|thanks|grateful|appreciate)",
                r"(?i)(this (helps|helped)|you (saved|help) me)",
                r"(?i)(so helpful|really appreciate|thankful)"
            ],
            "creative_request_patterns": [
                r"(?i)(create|write|generate|make|design|build)",
                r"(?i)(story|poem|song|art|creative|imagine)",
                r"(?i)(brainstorm|ideas|creative thinking|innovative)"
            ],
            "complex_question_patterns": [
                r"(?i)(explain|analyze|compare|evaluate|discuss)",
                r"(?i)(why|how|what if|suppose|consider)",
                r"(?i)(complex|complicated|difficult|challenging)"
            ],
            "personal_sharing_patterns": [
                r"(?i)(my (life|family|relationship|experience))",
                r"(?i)(i (feel|felt|think|believe|experience))",
                r"(?i)(personal|private|intimate|secret)"
            ]
        }
    
    def detect_events_from_text(self, user_input: str, ai_response: str = "", 
                              context: Dict[str, Any] = None) -> List[EventType]:
        """
        Mendeteksi event dari teks input pengguna dan respons AI
        
        Args:
            user_input: Input dari pengguna
            ai_response: Respons dari AI (opsional)
            context: Konteks tambahan
            
        Returns:
            List of detected events
        """
        detected_events = []
        
        if not self.config.get("pattern_matching_enabled", True):
            return detected_events
            
        # Gabungkan input dan response untuk analisis
        combined_text = f"{user_input} {ai_response}".lower()
        
        # Deteksi pattern-based events
        for event_category, patterns in self.pattern_matchers.items():
            for pattern in patterns:
                if re.search(pattern, combined_text):
                    event_type = self._map_pattern_to_event(event_category, user_input, context)
                    if event_type and event_type not in detected_events:
                        detected_events.append(event_type)
                        break
        
        # Deteksi interaction pattern events
        interaction_events = self._detect_interaction_patterns(user_input, context)
        detected_events.extend(interaction_events)
        
        # Deteksi task completion events
        task_events = self._detect_task_events(user_input, ai_response, context)
        detected_events.extend(task_events)
        
        return list(set(detected_events))  # Remove duplicates
    
    def _map_pattern_to_event(self, pattern_category: str, user_input: str, 
                            context: Dict[str, Any] = None) -> Optional[EventType]:
        """Memetakan kategori pattern ke event type"""
        mapping = {
            "praise_patterns": EventType.USER_PRAISE,
            "criticism_patterns": EventType.USER_CRITICISM,
            "confusion_patterns": EventType.CONFUSION_DETECTED,
            "humor_patterns": EventType.HUMOR_DETECTED,
            "sadness_patterns": EventType.SADNESS_DETECTED,
            "excitement_patterns": EventType.EXCITEMENT_DETECTED,
            "gratitude_patterns": EventType.GRATITUDE_RECEIVED,
            "creative_request_patterns": EventType.CREATIVE_REQUEST,
            "complex_question_patterns": EventType.COMPLEX_QUESTION,
            "personal_sharing_patterns": EventType.PERSONAL_SHARING
        }
        
        return mapping.get(pattern_category)
    
    def _detect_interaction_patterns(self, user_input: str, 
                                   context: Dict[str, Any] = None) -> List[EventType]:
        """Mendeteksi pattern interaksi"""
        events = []
        current_time = time.time()
        
        # Deteksi rapid interaction
        time_since_last = current_time - self.last_interaction_time
        if time_since_last < 5:  # Kurang dari 5 detik
            events.append(EventType.RAPID_INTERACTION)
        elif time_since_last > 180:  # Lebih dari 3 menit
            events.append(EventType.LONG_SILENCE)
        
        # Update interaction tracking
        self.last_interaction_time = current_time
        self.interaction_count += 1
        
        # Deteksi berdasarkan panjang input
        if len(user_input.split()) < 5:
            events.append(EventType.SIMPLE_QUESTION)
        elif len(user_input.split()) > 20:
            events.append(EventType.COMPLEX_QUESTION)
            
        return events
    
    def _detect_task_events(self, user_input: str, ai_response: str, 
                          context: Dict[str, Any] = None) -> List[EventType]:
        """Mendeteksi event terkait penyelesaian tugas"""
        events = []
        
        if not context:
            return events
            
        # Deteksi successful task completion
        task_indicators = context.get("task_indicators", {})
        if task_indicators.get("completed", False):
            if task_indicators.get("user_satisfied", True):
                events.append(EventType.SUCCESSFUL_TASK)
            else:
                events.append(EventType.FAILED_TASK)
                
        # Deteksi new learning opportunities
        if context.get("contains_new_information", False):
            events.append(EventType.NEW_LEARNING)
            
        # Deteksi technical discussion
        technical_keywords = ["algorithm", "code", "programming", "technical", "system", "implementation"]
        if any(keyword in user_input.lower() for keyword in technical_keywords):
            events.append(EventType.TECHNICAL_DISCUSSION)
            
        return events
    
    def process_event(self, event_type: EventType, context: Dict[str, Any] = None, 
                     user_input: str = "", ai_response: str = "") -> bool:
        """
        Memproses event dan memicu emosi yang sesuai
        
        Args:
            event_type: Jenis event yang terjadi
            context: Konteks event
            user_input: Input pengguna terkait
            ai_response: Respons AI terkait
            
        Returns:
            True jika emosi berhasil dipicu, False jika tidak
        """
        # Cari trigger yang sesuai
        matching_triggers = [t for t in self.triggers if t.event_type == event_type]
        
        if not matching_triggers:
            return False
            
        # Cek cooldown
        if self._is_in_cooldown(event_type):
            return False
            
        for trigger in matching_triggers:
            # Cek kondisi trigger
            if not self._check_trigger_conditions(trigger, context, user_input):
                continue
                
            # Hitung intensitas dan durasi
            intensity = self._calculate_trigger_intensity(trigger, context, user_input)
            duration = self._calculate_trigger_duration(trigger, context)
            
            # Cek threshold minimum
            if intensity < self.config.get("trigger_sensitivity", 0.7) * 0.5:
                continue
                
            # Tambahkan emosi - Menggunakan method yang sesuai
            try:
                self.emotion_manager.add_emotion(
                    emotion_type=trigger.emotion_type,
                    intensity=intensity,
                    duration=duration,
                    trigger_source=f"event_{event_type.value}",
                    context={
                        "event_type": event_type.value,
                        "user_input": user_input[:100] if user_input else "",  # Limit length
                        "trigger_context": context or {},
                        "timestamp": time.time()
                    }
                )
            except AttributeError:
                # Fallback jika add_emotion tidak ada
                try:
                    self.emotion_manager.trigger_emotion(
                        emotion_type=trigger.emotion_type,
                        intensity=intensity,
                        duration=duration
                    )
                except AttributeError:
                    # Fallback terakhir - update state saja
                    self.emotion_manager.update_state({
                        "primary_emotion": trigger.emotion_type.value,
                        "intensity": intensity,
                        "source": f"event_{event_type.value}"
                    })
            
            # Catat event
            self._record_event(event_type, intensity, context)
            
            return True
            
        return False
    
    def _is_in_cooldown(self, event_type: EventType) -> bool:
        """Cek apakah event masih dalam cooldown period"""
        cooldown_config = self.config.get("trigger_cooldown", {})
        cooldown_duration = cooldown_config.get(event_type.value, 0)
        
        if cooldown_duration == 0:
            return False
            
        current_time = time.time()
        
        # Cek recent events
        for event_record in reversed(self.event_history):
            if event_record["event_type"] == event_type.value:
                if current_time - event_record["timestamp"] < cooldown_duration:
                    return True
                break
                
        return False
    
    def _check_trigger_conditions(self, trigger: EventTrigger, context: Dict[str, Any] = None,
                                user_input: str = "") -> bool:
        """Cek apakah kondisi trigger terpenuhi"""
        if not trigger.conditions:
            return True
            
        context = context or {}
        
        # Cek context requirements
        for requirement in trigger.context_requirements:
            if requirement not in context:
                return False
                
        # Cek kondisi spesifik
        for condition_key, condition_value in trigger.conditions.items():
            if condition_key == "min_input_length":
                if len(user_input.split()) < condition_value:
                    return False
            elif condition_key == "max_input_length":
                if len(user_input.split()) > condition_value:
                    return False
            elif condition_key == "required_keywords":
                if not any(keyword.lower() in user_input.lower() for keyword in condition_value):
                    return False
            elif condition_key == "context_value":
                if context.get(condition_key) != condition_value:
                    return False
                    
        return True
    
    def _calculate_trigger_intensity(self, trigger: EventTrigger, context: Dict[str, Any] = None,
                                   user_input: str = "") -> float:
        """Menghitung intensitas emosi berdasarkan trigger"""
        base_intensity = trigger.intensity_base
        context = context or {}
        
        # Terapkan base sensitivity
        intensity = base_intensity * self.config.get("trigger_sensitivity", 0.7)
        
        # Terapkan modifiers
        for modifier_key, modifier_value in trigger.intensity_modifiers.items():
            if modifier_key == "repetition":
                # Kurangi intensitas untuk event berulang
                recent_same_events = self._count_recent_events(trigger.event_type, 300)  # 5 menit
                if recent_same_events > 0:
                    intensity *= (modifier_value ** recent_same_events)
                    
            elif modifier_key == "specificity":
                # Tingkatkan intensitas untuk input yang spesifik
                if len(user_input.split()) > 10:
                    intensity *= modifier_value
                    
            elif modifier_key == "context_bonus":
                # Bonus berdasarkan konteks
                if context.get("user_satisfaction", 0) > 0.8:
                    intensity *= modifier_value
                    
            elif modifier_key == "complexity":
                # Modifier berdasarkan kompleksitas
                complexity_score = context.get("complexity_score", 0.5)
                intensity *= (1 + (complexity_score - 0.5) * modifier_value)
                
            elif modifier_key == "user_distress_level":
                # Modifier berdasarkan tingkat distress pengguna
                distress_level = context.get("user_distress", 0.5)
                intensity *= (1 + distress_level * modifier_value)
                
        # Terapkan adaptive intensity jika diaktifkan
        if self.config.get("adaptive_intensity", True):
            intensity = self._apply_adaptive_intensity(intensity, trigger.event_type, context)
            
        # Pastikan dalam rentang yang valid
        return max(0.1, min(1.0, intensity))
    
    def _calculate_trigger_duration(self, trigger: EventTrigger, context: Dict[str, Any] = None) -> float:
        """Menghitung durasi emosi berdasarkan trigger"""
        base_duration = trigger.duration_base
        context = context or {}
        
        # Modifikasi durasi berdasarkan konteks
        duration_modifier = 1.0
        
        # Durasi lebih lama untuk emosi positif jika ada indikasi kepuasan tinggi
        if (trigger.emotion_type in [EmotionType.JOY, EmotionType.EXCITEMENT] and 
            context.get("user_satisfaction", 0) > 0.8):
            duration_modifier *= 1.3
            
        # Durasi lebih pendek untuk emosi negatif jika ada resolusi cepat
        if (trigger.emotion_type in [EmotionType.SADNESS, EmotionType.ANGER] and 
            context.get("quick_resolution", False)):
            duration_modifier *= 0.7
            
        return base_duration * duration_modifier
    
    def _apply_adaptive_intensity(self, intensity: float, event_type: EventType, 
                                context: Dict[str, Any]) -> float:
        """Menerapkan penyesuaian intensitas adaptif"""
        # Analisis tren emosi terkini
        try:
            current_emotions = self.emotion_manager.get_current_emotional_state()
        except AttributeError:
            # Fallback jika method tidak ada
            try:
                current_emotions = self.emotion_manager.get_current_state()
            except AttributeError:
                current_emotions = {"emotions": [], "mood": {"type": "neutral"}}
        
        # Kurangi intensitas jika sudah ada emosi serupa yang kuat
        emotions_list = current_emotions.get("emotions", [])
        if isinstance(emotions_list, list):
            for emotion_data in emotions_list:
                if isinstance(emotion_data, dict) and emotion_data.get("intensity", 0) > 0.7:
                    # Ada emosi kuat, kurangi intensitas emosi baru
                    intensity *= 0.8
                    break
                    
        # Tingkatkan intensitas jika mood mendukung
        current_mood = current_emotions.get("mood", {}).get("type", "neutral")
        
        mood_synergy = {
            "cheerful": [EventType.USER_PRAISE, EventType.SUCCESSFUL_TASK, EventType.HUMOR_DETECTED],
            "contemplative": [EventType.COMPLEX_QUESTION, EventType.NEW_LEARNING],
            "supportive": [EventType.PERSONAL_SHARING, EventType.SADNESS_DETECTED]
        }
        
        for mood, synergistic_events in mood_synergy.items():
            if current_mood == mood and event_type in synergistic_events:
                intensity *= 1.2
                break
                
        return intensity
    
    def _count_recent_events(self, event_type: EventType, time_window: float) -> int:
        """Menghitung jumlah event serupa dalam periode waktu tertentu"""
        current_time = time.time()
        count = 0
        
        for event_record in reversed(self.event_history):
            if current_time - event_record["timestamp"] > time_window:
                break
            if event_record["event_type"] == event_type.value:
                count += 1
                
        return count
    
    def _record_event(self, event_type: EventType, intensity: float, 
                     context: Dict[str, Any] = None) -> None:
        """Mencatat event ke riwayat"""
        event_record = {
            "event_type": event_type.value,
            "intensity": intensity,
            "timestamp": time.time(),
            "context": context or {}
        }
        
        self.event_history.append(event_record)
        
        # Batasi ukuran riwayat
        max_history = 100
        if len(self.event_history) > max_history:
            self.event_history = self.event_history[-max_history:]
    
    def process_user_interaction(self, user_input: str, ai_response: str = "",
                               context: Dict[str, Any] = None) -> List[EventType]:
        """
        Memproses interaksi pengguna secara keseluruhan
        
        Args:
            user_input: Input dari pengguna
            ai_response: Respons dari AI
            context: Konteks interaksi
            
        Returns:
            List of events that were processed
        """
        # Deteksi events dari teks
        detected_events = self.detect_events_from_text(user_input, ai_response, context)
        
        # Proses setiap event yang terdeteksi
        processed_events = []
        for event_type in detected_events:
            if self.process_event(event_type, context, user_input, ai_response):
                processed_events.append(event_type)
                
        return processed_events
    
    def add_custom_trigger(self, trigger: EventTrigger) -> None:
        """Menambahkan trigger kustom"""
        self.triggers.append(trigger)
    
    def remove_trigger(self, event_type: EventType, emotion_type: EmotionType = None) -> bool:
        """Menghapus trigger berdasarkan event type dan/atau emotion type"""
        initial_count = len(self.triggers)
        
        self.triggers = [
            t for t in self.triggers 
            if not (t.event_type == event_type and 
                   (emotion_type is None or t.emotion_type == emotion_type))
        ]
        
        return len(self.triggers) < initial_count
    
    def get_trigger_statistics(self) -> Dict[str, Any]:
        """Mendapatkan statistik trigger"""
        # Hitung frekuensi event
        event_counts = {}
        current_time = time.time()
        total_intensity = {}
        
        for event_record in self.event_history:
            event_type = event_record["event_type"]
            intensity = event_record.get("intensity", 0.0)
            
            if event_type not in event_counts:
                event_counts[event_type] = {"total": 0, "recent": 0, "avg_intensity": 0.0}
                total_intensity[event_type] = []
                
            event_counts[event_type]["total"] += 1
            total_intensity[event_type].append(intensity)
            
            # Count recent events (last hour)
            if current_time - event_record["timestamp"] < 3600:
                event_counts[event_type]["recent"] += 1
        
        # Calculate average intensity for each event type
        for event_type in event_counts:
            if total_intensity[event_type]:
                event_counts[event_type]["avg_intensity"] = sum(total_intensity[event_type]) / len(total_intensity[event_type])
        
        # Hitung statistik umum
        total_events = len(self.event_history)
        recent_events = sum(1 for record in self.event_history 
                          if current_time - record["timestamp"] < 3600)
        
        # Temukan event paling sering
        most_frequent_event = None
        max_count = 0
        for event_type, stats in event_counts.items():
            if stats["total"] > max_count:
                max_count = stats["total"]
                most_frequent_event = event_type
        
        # Hitung rata-rata interval antar event
        avg_interval = 0.0
        if len(self.event_history) > 1:
            intervals = []
            sorted_events = sorted(self.event_history, key=lambda x: x["timestamp"])
            for i in range(1, len(sorted_events)):
                interval = sorted_events[i]["timestamp"] - sorted_events[i-1]["timestamp"]
                intervals.append(interval)
            if intervals:
                avg_interval = sum(intervals) / len(intervals)
        
        # Hitung distribusi emosi yang dipicu
        emotion_distribution = {}
        for trigger in self.triggers:
            emotion_type = trigger.emotion_type.value
            if emotion_type not in emotion_distribution:
                emotion_distribution[emotion_type] = 0
            # Hitung berapa kali emosi ini dipicu berdasarkan event history
            for event_record in self.event_history:
                if any(t.event_type.value == event_record["event_type"] and 
                      t.emotion_type.value == emotion_type for t in self.triggers):
                    emotion_distribution[emotion_type] += 1
                    break
        
        # Analisis tren temporal
        recent_24h = [record for record in self.event_history 
                     if current_time - record["timestamp"] < 86400]
        hourly_distribution = {}
        for i in range(24):
            hourly_distribution[i] = 0
        
        for record in recent_24h:
            hour = int((current_time - record["timestamp"]) // 3600)
            if hour < 24:
                hourly_distribution[23-hour] += 1  # 0 = current hour
        
        # Efektivitas trigger (berapa persen event yang berhasil memicu emosi)
        successful_triggers = len([record for record in self.event_history 
                                 if record.get("intensity", 0) > 0])
        trigger_effectiveness = (successful_triggers / total_events * 100) if total_events > 0 else 0
        
        return {
            "total_events": total_events,
            "recent_events_1h": recent_events,
            "event_frequency": event_counts,
            "most_frequent_event": most_frequent_event,
            "avg_event_interval_seconds": avg_interval,
            "emotion_distribution": emotion_distribution,
            "hourly_distribution": hourly_distribution,
            "trigger_effectiveness_percent": trigger_effectiveness,
            "active_triggers_count": len(self.triggers),
            "session_stats": {
                "interaction_count": self.interaction_count,
                "session_duration_seconds": current_time - self.last_interaction_time if hasattr(self, 'session_start_time') else 0,
                "avg_interactions_per_minute": (self.interaction_count / ((current_time - self.last_interaction_time) / 60)) if self.interaction_count > 0 else 0
            },
            "config_status": {
                "sensitivity": self.config.get("trigger_sensitivity", 0.7),
                "pattern_matching_enabled": self.config.get("pattern_matching_enabled", True),
                "adaptive_intensity": self.config.get("adaptive_intensity", True),
                "event_accumulation": self.config.get("event_accumulation", True)
            }
        }
    
    def cleanup_old_events(self, max_age_seconds: float = None) -> int:
        """
        Membersihkan event lama dari history
        
        Args:
            max_age_seconds: Usia maksimum event dalam detik (default dari config)
            
        Returns:
            Jumlah event yang dihapus
        """
        if max_age_seconds is None:
            max_age_seconds = self.config.get("event_memory_duration", 300)
            
        current_time = time.time()
        initial_count = len(self.event_history)
        
        self.event_history = [
            record for record in self.event_history
            if current_time - record["timestamp"] <= max_age_seconds
        ]
        
        return initial_count - len(self.event_history)
    
    def reset_session(self) -> None:
        """Reset session data dan statistics"""
        self.event_history.clear()
        self.interaction_count = 0
        self.last_interaction_time = time.time()
        self.session_context.clear()
    
    def export_event_history(self, filepath: str = None) -> Dict[str, Any]:
        """
        Export event history untuk analisis atau backup
        
        Args:
            filepath: Path file untuk menyimpan (opsional)
            
        Returns:
            Dictionary berisi event history dan metadata
        """
        export_data = {
            "export_timestamp": time.time(),
            "config": self.config,
            "event_history": self.event_history,
            "statistics": self.get_trigger_statistics(),
            "active_triggers": [
                {
                    "event_type": trigger.event_type.value,
                    "emotion_type": trigger.emotion_type.value,
                    "intensity_base": trigger.intensity_base,
                    "duration_base": trigger.duration_base,
                    "conditions": trigger.conditions,
                    "intensity_modifiers": trigger.intensity_modifiers
                }
                for trigger in self.triggers
            ]
        }
        
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"Error exporting event history: {e}")
                
        return export_data
    
    def import_event_history(self, filepath: str) -> bool:
        """
        Import event history dari file backup
        
        Args:
            filepath: Path file backup
            
        Returns:
            True jika berhasil, False jika gagal
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
                
            # Validasi data
            if "event_history" not in import_data:
                return False
                
            # Import event history
            self.event_history = import_data["event_history"]
            
            # Import config jika ada
            if "config" in import_data:
                self.config.update(import_data["config"])
                
            return True
            
        except Exception as e:
            print(f"Error importing event history: {e}")
            return False

# Contoh penggunaan dan testing
if __name__ == "__main__":
    # Mock EmotionalStateManager untuk testing
    class MockEmotionalStateManager:
        def __init__(self):
            self.current_state = {"mood": {"type": "neutral"}, "emotions": []}
        
        def add_emotion(self, emotion_type, intensity, duration, trigger_source=None, context=None):
            print(f"Mock: Adding emotion {emotion_type.value} with intensity {intensity}")
        
        def get_current_emotional_state(self):
            return self.current_state
        
        def get_current_state(self):
            return self.current_state
    
    # Test basic functionality
    print("🧪 Testing EventEmotionTrigger...")
    
    mock_manager = MockEmotionalStateManager()
    trigger_system = EventEmotionTrigger(mock_manager)
    
    # Test event detection
    test_inputs = [
        "Thank you so much! This is amazing!",
        "I'm really confused about this...",
        "That's hilarious! Made me laugh!",
        "I'm feeling quite sad today",
        "Can you help me create a story?"
    ]
    
    for test_input in test_inputs:
        print(f"\nInput: {test_input}")
        detected_events = trigger_system.detect_events_from_text(test_input)
        print(f"Detected events: {[e.value for e in detected_events]}")
        
        # Process the events
        for event in detected_events:
            success = trigger_system.process_event(event, user_input=test_input)
            print(f"Processed {event.value}: {'✅' if success else '❌'}")
    
    # Print statistics
    print("\n📊 Trigger Statistics:")
    stats = trigger_system.get_trigger_statistics()
    print(f"Total events: {stats['total_events_processed']}")
    print(f"Interaction count: {stats['interaction_count']}")
    
    print("\n✅ EventEmotionTrigger testing completed!")