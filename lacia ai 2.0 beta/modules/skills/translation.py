#!/usr/bin/env python3
# translation.py - Modul keterampilan terjemahan

from typing import Dict, List, Any, Tuple
import re

class TranslationSkill:
    """
    Keterampilan untuk menerjemahkan teks antar bahasa
    menggunakan model dasar
    """
    
    def __init__(self, config=None):
        """
        Inisialisasi keterampilan terjemahan
        
        Args:
            config: Konfigurasi untuk keterampilan ini
        """
        if config is None:
            config = {}
            
        self.config = config
        
        # Daftar bahasa yang didukung
        self.supported_languages = {
            "id": "Indonesian",
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "ja": "Japanese",
            "ko": "Korean",
            "zh": "Chinese",
            "ar": "Arabic",
            "ru": "Russian",
            "pt": "Portuguese",
            "nl": "Dutch",
            "tr": "Turkish",
            "pl": "Polish",
            "sv": "Swedish"
        }
    
    def translate(self, text: str, source_lang: str = None, target_lang: str = "en") -> Dict[str, Any]:
        """
        Terjemahkan teks ke bahasa target
        
        Args:
            text: Teks yang akan diterjemahkan
            source_lang: Kode bahasa sumber (opsional, otomatis deteksi jika None)
            target_lang: Kode bahasa target
            
        Returns:
            Dict berisi hasil terjemahan
        """
        # Deteksi bahasa sumber jika tidak ditentukan
        if source_lang is None:
            source_lang = self._detect_language(text)
            
        # Validasi bahasa
        source_name = self.supported_languages.get(source_lang, "Unknown")
        target_name = self.supported_languages.get(target_lang, "Unknown")
        
        if source_lang not in self.supported_languages:
            return {
                "success": False,
                "error": f"Bahasa sumber '{source_lang}' tidak didukung",
                "supported_languages": list(self.supported_languages.keys())
            }
            
        if target_lang not in self.supported_languages:
            return {
                "success": False,
                "error": f"Bahasa target '{target_lang}' tidak didukung",
                "supported_languages": list(self.supported_languages.keys())
            }
            
        # Tidak perlu terjemahan jika bahasa sama
        if source_lang == target_lang:
            return {
                "success": True,
                "translated_text": text,
                "source_language": source_lang,
                "source_language_name": source_name,
                "target_language": target_lang,
                "target_language_name": target_name,
                "confidence": 1.0
            }
        
        # Dalam implementasi sebenarnya, saat ini akan menggunakan model LLM utama
        # untuk melakukan terjemahan. Di sini kita hanya memformat permintaan.
        
        prompt = f"""Translate the following text from {source_name} to {target_name}:

{text}

Translation:"""

        # Catatan: Dalam implementasi sebenarnya, kita akan meneruskan prompt ini
        # ke model utama untuk mendapatkan terjemahan. Untuk contoh ini, kita
        # menggunakan pengganti sederhana untuk mensimulasikan terjemahan.
        
        # Hasil terjemahan "dummy" untuk tujuan demonstrasi
        translated_text = f"[Terjemahan dari {source_name} ke {target_name}] {text[:100]}" + \
                         ("..." if len(text) > 100 else "")
        
        return {
            "success": True,
            "original_text": text,
            "translated_text": translated_text,
            "source_language": source_lang,
            "source_language_name": source_name,
            "target_language": target_lang,
            "target_language_name": target_name,
            "prompt": prompt,
            "confidence": 0.85
        }
    
    def _detect_language(self, text: str) -> str:
        """
        Deteksi bahasa teks (implementasi sederhana)
        
        Args:
            text: Teks untuk deteksi bahasa
            
        Returns:
            str: Kode bahasa yang terdeteksi
        """
        # Implementasi sederhana untuk contoh
        text_lower = text.lower()
        
        # Kata-kata khas Indonesia
        id_words = ["yang", "dengan", "untuk", "dari", "ini", "itu", "dan", "atau", "jika", "maka"]
        # Kata-kata khas Inggris
        en_words = ["the", "and", "for", "this", "that", "with", "from", "what", "when", "where"]
        # Kata-kata khas Spanyol
        es_words = ["el", "la", "los", "las", "que", "para", "por", "con", "este", "esta"]
        
        # Hitung kemunculan kata-kata
        id_count = sum(1 for word in id_words if f" {word} " in f" {text_lower} ")
        en_count = sum(1 for word in en_words if f" {word} " in f" {text_lower} ")
        es_count = sum(1 for word in es_words if f" {word} " in f" {text_lower} ")
        
        # Pilih bahasa dengan hitungan tertinggi
        counts = {"id": id_count, "en": en_count, "es": es_count}
        max_lang = max(counts, key=counts.get)
        
        # Default ke bahasa Inggris jika tidak ada yang cocok
        if counts[max_lang] == 0:
            return "en"
            
        return max_lang
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Mendapatkan daftar bahasa yang didukung
        
        Returns:
            Dict berisi kode bahasa dan nama bahasa
        """
        return self.supported_languages
