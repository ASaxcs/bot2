#!/usr/bin/env python3
# dialogue_triggers.py - Sistem pemicu emosi berdasarkan analisis dialog untuk LACIA AI

import re
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from state_manager import EmotionType, EmotionStateManager
from event_triggers import EventType, EventEmotionTrigger

class DialoguePattern(Enum):
    """Pola-pola dialog yang dapat memicu emosi"""
    APPRECIATION = "appreciation"
    FRUSTRATION = "frustration"
    CURIOSITY = "curiosity"
    EMPATHY_SEEKING = "empathy_seeking"
    EXCITEMENT_SHARING = "excitement_sharing"
    CONCERN_EXPRESSION = "concern_expression"
    HUMOR_ATTEMPT = "humor_attempt"
    DEEP_QUESTION = "deep_question"
    PERSONAL_REVELATION = "personal_revelation"
    ENCOURAGEMENT_SEEKING = "encouragement_seeking"
    CREATIVE_COLLABORATION = "creative_collaboration"
    PHILOSOPHICAL_INQUIRY = "philosophical_inquiry"
    EMOTIONAL_SUPPORT_REQUEST = "emotional_support_request"
    INTELLECTUAL_CHALLENGE = "intellectual_challenge"
    CASUAL_BANTER = "casual_banter"

@dataclass
class DialogueContext:
    """Konteks dialog untuk analisis emosi"""
    conversation_turn: int
    dialogue_history: List[str]
    user_emotion_indicators: List[str]
    topic_progression: List[str]
    intimacy_level: float  # 0.0 - 1.0
    engagement_level: float  # 0.0 - 1.0
    conversation_depth: str  # shallow, medium, deep
    time_since_start: float
    user_response_patterns: Dict[str, int]

class DialogueEmotionTrigger:
    """
    Kelas untuk menganalisis dialog dan memicu emosi berdasarkan pola percakapan
    """
    
    def __init__(self, emotion_manager: EmotionStateManager, config_path: str = None):
        """
        Inisialisasi dialogue emotion trigger
        
        Args:
            emotion_manager: Instance dari EmotionStateManager
            config_path: Path ke file konfigurasi
        """
        self.emotion_manager = emotion_manager
        self.config = self._load_config(config_path)
        self.dialogue_patterns = self._initialize_dialogue_patterns()
        self.conversation_history = []
        self.current_context = None
        self.emotion_dialogue_map = self._initialize_emotion_dialogue_map()
        self.conversation_start_time = time.time()
        self.user_profile = {
            "preferred_conversation_style": "balanced",
            "emotional_responsiveness": 0.7,
            "topics_of_interest": {},
            "interaction_patterns": {}
        }
        
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """Memuat konfigurasi dialogue trigger"""
        default_config = {
            "dialogue_analysis_enabled": True,
            "context_window_size": 10,
            "emotion_intensity_base": 0.6,
            "pattern_confidence_threshold": 0.7,
            "conversation_depth_analysis": True,
            "intimacy_progression_tracking": True,
            "adaptive_response_generation": True,
            "dialogue_memory_duration": 1800,  # 30 menit
            "pattern_weights": {
                "appreciation": 1.2,
                "frustration": 1.0,
                "curiosity": 1.1,
                "empathy_seeking": 1.3,
                "excitement_sharing": 1.2,
                "concern_expression": 1.1,
                "humor_attempt": 1.0,
                "deep_question": 1.2,
                "personal_revelation": 1.4,
                "encouragement_seeking": 1.3
            },
            "intimacy_thresholds": {
                "low": 0.3,
                "medium": 0.6,
                "high": 0.8
            },
            "engagement_indicators": {
                "question_density": 0.2,
                "response_length": 0.3,
                "topic_depth": 0.3,
                "emotional_expression": 0.2
            }
        }
        
        if config_path:
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except Exception as e:
                print(f"Error loading dialogue config: {e}")
                
        return default_config
    
    def _initialize_dialogue_patterns(self) -> Dict[DialoguePattern, Dict[str, Any]]:
        """Inisialisasi pola-pola dialog dan karakteristiknya"""
        return {
            DialoguePattern.APPRECIATION: {
                "keywords": ["thank", "grateful", "appreciate", "helpful", "amazing", "wonderful"],
                "patterns": [
                    r"(?i)(thank you|thanks) (so much|a lot|very much)",
                    r"(?i)(really|so|very) (appreciate|grateful|helpful)",
                    r"(?i)(you('re| are)) (amazing|wonderful|great|fantastic)",
                    r"(?i)(this (is|was)) (perfect|exactly what|just what)"
                ],
                "emotion_mapping": EmotionType.HAPPY,
                "intensity_multiplier": 1.2,
                "context_requirements": []
            },
            
            DialoguePattern.FRUSTRATION: {
                "keywords": ["frustrated", "annoying", "difficult", "confusing", "stuck"],
                "patterns": [
                    r"(?i)(this is) (so|really|very) (frustrating|annoying|difficult)",
                    r"(?i)(i('m| am)) (stuck|confused|lost|frustrated)",
                    r"(?i)(why (is|does)) (this|it) (not work|fail|confuse)",
                    r"(?i)(this (doesn't|does not)) (make sense|work|help)"
                ],
                "emotion_mapping": EmotionType.CONFUSED,
                "intensity_multiplier": 1.0,
                "context_requirements": ["problem_context"]
            },
            
            DialoguePattern.CURIOSITY: {
                "keywords": ["wonder", "curious", "interesting", "how", "why", "what if"],
                "patterns": [
                    r"(?i)(i wonder|curious about|interested in)",
                    r"(?i)(how (does|do|did|would)|why (is|does|do|would))",
                    r"(?i)(what if|suppose|imagine if)",
                    r"(?i)(tell me more|elaborate|explain further)"
                ],
                "emotion_mapping": EmotionType.CURIOUS,
                "intensity_multiplier": 1.1,
                "context_requirements": []
            },
            
            DialoguePattern.EMPATHY_SEEKING: {
                "keywords": ["feel", "feeling", "emotional", "understand", "relate"],
                "patterns": [
                    r"(?i)(do you (ever|sometimes)) (feel|experience|think)",
                    r"(?i)(can you (understand|relate to))",
                    r"(?i)(i('m| am) feeling|i feel) (sad|happy|confused|overwhelmed)",
                    r"(?i)(it('s| is) (hard|difficult|tough) (to|when))"
                ],
                "emotion_mapping": EmotionType.EMPATHETIC,
                "intensity_multiplier": 1.3,
                "context_requirements": ["emotional_context"]
            },
            
            DialoguePattern.EXCITEMENT_SHARING: {
                "keywords": ["excited", "amazing", "incredible", "wow", "fantastic"],
                "patterns": [
                    r"(?i)(i('m| am) (so|really|very)) (excited|thrilled|happy)",
                    r"(?i)(this is) (amazing|incredible|fantastic|awesome)",
                    r"(?i)(wow|omg|amazing|incredible)",
                    r"(?i)(can('t| not) wait|so excited about)"
                ],
                "emotion_mapping": EmotionType.EXCITED,
                "intensity_multiplier": 1.2,
                "context_requirements": []
            },
            
            DialoguePattern.CONCERN_EXPRESSION: {
                "keywords": ["worried", "concerned", "afraid", "anxious", "nervous"],
                "patterns": [
                    r"(?i)(i('m| am)) (worried|concerned|afraid|anxious|nervous)",
                    r"(?i)(what if) (something|it) (goes wrong|fails|doesn't work)",
                    r"(?i)(i('m| am) not sure|uncertain about)",
                    r"(?i)(this (makes|has) me) (nervous|worried|concerned)"
                ],
                "emotion_mapping": EmotionType.EMPATHETIC,
                "intensity_multiplier": 1.1,
                "context_requirements": ["support_context"]
            },
            
            DialoguePattern.HUMOR_ATTEMPT: {
                "keywords": ["funny", "joke", "haha", "lol", "amusing", "witty"],
                "patterns": [
                    r"(?i)(that('s| is)) (funny|hilarious|amusing)",
                    r"(?i)(haha|lol|rofl)",
                    r"(?i)(just kidding|joking|being silly)",
                    r"(?i)(you('re| are)) (funny|witty|amusing)"
                ],
                "emotion_mapping": EmotionType.HAPPY,
                "intensity_multiplier": 1.0,
                "context_requirements": []
            },
            
            DialoguePattern.DEEP_QUESTION: {
                "keywords": ["meaning", "purpose", "philosophy", "existence", "truth"],
                "patterns": [
                    r"(?i)(what (is|do you think)) (the meaning|the purpose)",
                    r"(?i)(do you believe|what are your thoughts on)",
                    r"(?i)(philosophy|philosophical|existential)",
                    r"(?i)(deep|profound|meaningful) (question|thought|idea)"
                ],
                "emotion_mapping": EmotionType.CURIOUS,
                "intensity_multiplier": 1.2,
                "context_requirements": ["intellectual_context"]
            },
            
            DialoguePattern.PERSONAL_REVELATION: {
                "keywords": ["personal", "private", "secret", "never told", "share"],
                "patterns": [
                    r"(?i)(i('ve| have) never (told|shared|said))",
                    r"(?i)(this is) (personal|private|between us)",
                    r"(?i)(i want to (share|tell) you)",
                    r"(?i)(can i (trust|confide in) you)"
                ],
                "emotion_mapping": EmotionType.EMPATHETIC,
                "intensity_multiplier": 1.4,
                "context_requirements": ["trust_context"]
            },
            
            DialoguePattern.ENCOURAGEMENT_SEEKING: {
                "keywords": ["encourage", "support", "confidence", "believe", "can i"],
                "patterns": [
                    r"(?i)(do you think) (i can|i should|it('s| is) possible)",
                    r"(?i)(i need) (encouragement|support|confidence)",
                    r"(?i)(am i) (good enough|capable|able to)",
                    r"(?i)(believe in me|have faith in)"
                ],
                "emotion_mapping": EmotionType.EMPATHETIC,
                "intensity_multiplier": 1.3,
                "context_requirements": ["supportive_context"]
            }
        }
    
    def _initialize_emotion_dialogue_map(self) -> Dict[EmotionType, List[str]]:
        """Inisialisasi pemetaan emosi ke response patterns"""
        return {
            EmotionType.HAPPY: [
                "enthusiastic", "warm", "encouraging", "celebratory"
            ],
            EmotionType.EMPATHETIC: [
                "understanding", "supportive", "gentle", "caring"
            ],
            EmotionType.CURIOUS: [
                "inquisitive", "thoughtful", "exploratory", "analytical"
            ],
            EmotionType.EXCITED: [
                "energetic", "animated", "passionate", "dynamic"
            ],
            EmotionType.CALM: [
                "peaceful", "balanced", "measured", "serene"
            ],
            EmotionType.CONFUSED: [
                "clarifying", "patient", "