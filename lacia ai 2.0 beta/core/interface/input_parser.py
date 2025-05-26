"""
Input Parser untuk antarmuka Lacia AI
Menangani parsing dan validasi input dari berbagai sumber
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

class InputType(Enum):
    """Tipe input yang didukung"""
    TEXT = "text"
    COMMAND = "command"
    QUESTION = "question"
    INSTRUCTION = "instruction"
    CONVERSATION = "conversation"
    FILE_UPLOAD = "file_upload"
    VOICE = "voice"
    UNKNOWN = "unknown"

class Intent(Enum):
    """Intent/niat dari input pengguna"""
    GREETING = "greeting"
    QUESTION = "question"
    REQUEST_INFO = "request_info"
    CREATIVE_TASK = "creative_task"
    PROBLEM_SOLVING = "problem_solving"
    CONVERSATION = "conversation"
    COMMAND = "command"
    GOODBYE = "goodbye"
    UNKNOWN = "unknown"

@dataclass
class ParsedInput:
    """Struktur hasil parsing input"""
    original_text: str
    cleaned_text: str
    input_type: InputType
    intent: Intent
    entities: Dict[str, Any]
    keywords: List[str]
    sentiment: str
    confidence: float
    metadata: Dict[str, Any]

class InputParser:
    """Parser untuk menganalisis dan memproses input pengguna"""
    
    def __init__(self, config=None):  
        # ^-- Baris 51 yang bermasalah
        self.config = config or {}  
        # Pastikan ada indentasi di sini
        
        # Inisialisasi pola-pola parsing
        self.greeting_patterns = [
            r"^(hai|halo|hello|hi|selamat\s+(pagi|siang|malam))",
            r"(apa\s+kabar|how\s+are\s+you)"
        ]
        
        self.question_patterns = [
            r"^(apa|siapa|dimana|kapan|mengapa|bagaimana|berapa)",
            r"^(what|who|where|when|why|how|which)",
            r".*\?$"
        ]
        
        self.command_patterns = [
            r"^(buatkan|buat|lakukan|jalankan|eksekusi)",
            r"^(create|make|do|run|execute)",
            r"^(/\w+)"  # Command dengan prefix /
        ]
        
        self.goodbye_patterns = [
            r"^(bye|goodbye|selamat\s+tinggal|sampai\s+jumpa)",
            r"(terima\s+kasih|thank\s+you).*"
        ]
        
        self.stop_words = {
            'dan', 'atau', 'tetapi', 'dengan', 'untuk', 'dari', 'ke', 'di', 'pada',
            'yang', 'adalah', 'akan', 'sudah', 'belum', 'tidak', 'jangan',
            'and', 'or', 'but', 'with', 'for', 'from', 'to', 'at', 'in', 'on',
            'the', 'is', 'are', 'was', 'were', 'will', 'would', 'should', 'could'
        }
    
    def parse(self, input_text: str, context: Optional[Dict[str, Any]] = None) -> ParsedInput:
        """Parse input utama"""
        if not input_text or not input_text.strip():
            return self._create_empty_result(input_text)
        
        # Bersihkan input
        cleaned_text = self._clean_input(input_text)
        
        # Deteksi tipe input
        input_type = self._detect_input_type(cleaned_text)
        
        # Deteksi intent
        intent = self._detect_intent(cleaned_text, input_type)
        
        # Ekstrak entitas
        entities = self._extract_entities(cleaned_text)
        
        # Ekstrak keywords
        keywords = self._extract_keywords(cleaned_text)
        
        # Analisis sentiment
        sentiment = self._analyze_sentiment(cleaned_text)
        
        # Hitung confidence
        confidence = self._calculate_confidence(input_type, intent, entities)
        
        # Metadata tambahan
        metadata = {
            "length": len(cleaned_text),
            "word_count": len(cleaned_text.split()),
            "has_punctuation": bool(re.search(r'[.!?]', cleaned_text)),
            "context": context or {}
        }
        
        return ParsedInput(
            original_text=input_text,
            cleaned_text=cleaned_text,
            input_type=input_type,
            intent=intent,
            entities=entities,
            keywords=keywords,
            sentiment=sentiment,
            confidence=confidence,
            metadata=metadata
        )
    
    def _clean_input(self, text: str) -> str:
        """Membersihkan input dari karakter yang tidak perlu"""
        # Hapus whitespace berlebih
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Normalisasi tanda baca
        text = re.sub(r'[.]{2,}', '...', text)
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        
        return text
    
    def _detect_input_type(self, text: str) -> InputType:
        """Deteksi tipe input"""
        text_lower = text.lower()
        
        # Check untuk command
        if any(re.search(pattern, text_lower) for pattern in self.command_patterns):
            return InputType.COMMAND
        
        # Check untuk question
        if any(re.search(pattern, text_lower) for pattern in self.question_patterns):
            return InputType.QUESTION
        
        # Check panjang untuk conversation vs instruction
        if len(text.split()) < 5:
            return InputType.CONVERSATION
        else:
            return InputType.INSTRUCTION
    
    def _detect_intent(self, text: str, input_type: InputType) -> Intent:
        """Deteksi intent dari input"""
        text_lower = text.lower()
        
        # Greeting
        if any(re.search(pattern, text_lower) for pattern in self.greeting_patterns):
            return Intent.GREETING
        
        # Goodbye
        if any(re.search(pattern, text_lower) for pattern in self.goodbye_patterns):
            return Intent.GOODBYE
        
        # Command
        if input_type == InputType.COMMAND:
            return Intent.COMMAND
        
        # Question
        if input_type == InputType.QUESTION:
            if re.search(r'(apa itu|what is|jelaskan|explain)', text_lower):
                return Intent.REQUEST_INFO
            else:
                return Intent.QUESTION
        
        # Creative task
        if re.search(r'(buatkan|buat|tulis|write|create|design)', text_lower):
            return Intent.CREATIVE_TASK
        
        # Problem solving
        if re.search(r'(bantu|help|solve|selesaikan|cara)', text_lower):
            return Intent.PROBLEM_SOLVING
        
        return Intent.CONVERSATION
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Ekstrak entitas dari teks"""
        entities = {}
        
        # Tanggal
        date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'
        dates = re.findall(date_pattern, text)
        if dates:
            entities['dates'] = dates
        
        # Waktu
        time_pattern = r'\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?'
        times = re.findall(time_pattern, text, re.IGNORECASE)
        if times:
            entities['times'] = times
        
        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            entities['emails'] = emails
        
        # URL
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        if urls:
            entities['urls'] = urls
        
        # Angka
        number_pattern = r'\b\d+(?:\.\d+)?\b'
        numbers = re.findall(number_pattern, text)
        if numbers:
            entities['numbers'] = numbers
        
        return entities
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Ekstrak kata kunci penting"""
        # Tokenisasi
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter stop words dan kata pendek
        keywords = [
            word for word in words 
            if word not in self.stop_words and len(word) > 2
        ]
        
        # Hitung frekuensi dan ambil yang paling sering
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort berdasarkan frekuensi
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, freq in sorted_words[:10]]  # Top 10 keywords
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analisis sentiment sederhana"""
        positive_words = [
            'bagus', 'baik', 'senang', 'suka', 'terima kasih', 'amazing', 
            'good', 'great', 'excellent', 'wonderful', 'fantastic'
        ]
        
        negative_words = [
            'buruk', 'jelek', 'tidak suka', 'kecewa', 'marah', 'bad', 
            'terrible', 'awful', 'horrible', 'disappointed', 'angry'
        ]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _calculate_confidence(self, input_type: InputType, intent: Intent, 
                            entities: Dict[str, Any]) -> float:
        """Hitung confidence score parsing"""
        confidence = 0.5  # Base confidence
        
        # Boost confidence berdasarkan input type
        if input_type != InputType.UNKNOWN:
            confidence += 0.2
        
        # Boost confidence berdasarkan intent
        if intent != Intent.UNKNOWN:
            confidence += 0.2
        
        # Boost confidence berdasarkan entitas yang ditemukan
        if entities:
            confidence += min(0.1 * len(entities), 0.3)
        
        return min(confidence, 1.0)
    
    def _create_empty_result(self, original_text: str) -> ParsedInput:
        """Buat hasil kosong untuk input yang tidak valid"""
        return ParsedInput(
            original_text=original_text or "",
            cleaned_text="",
            input_type=InputType.UNKNOWN,
            intent=Intent.UNKNOWN,
            entities={},
            keywords=[],
            sentiment="neutral",
            confidence=0.0,
            metadata={"error": "empty_input"}
        )
    
    def get_response_suggestions(self, parsed_input: ParsedInput) -> List[str]:
        """Berikan saran respons berdasarkan input yang diparsing"""
        suggestions = []
        
        if parsed_input.intent == Intent.GREETING:
            suggestions = [
                "Berikan salam balik yang ramah",
                "Tanyakan apa yang bisa dibantu",
                "Tunjukkan antusiasme untuk membantu"
            ]
        elif parsed_input.intent == Intent.QUESTION:
            suggestions = [
                "Berikan jawaban yang informatif",
                "Minta klarifikasi jika pertanyaan tidak jelas",
                "Berikan contoh jika diperlukan"
            ]
        elif parsed_input.intent == Intent.CREATIVE_TASK:
            suggestions = [
                "Tanyakan detail lebih lanjut",
                "Berikan beberapa opsi kreatif",
                "Mulai dengan outline atau konsep"
            ]
        elif parsed_input.intent == Intent.PROBLEM_SOLVING:
            suggestions = [
                "Analisis masalah step by step",
                "Berikan beberapa solusi alternatif",
                "Tanyakan informasi tambahan yang diperlukan"
            ]
        
        return suggestions
