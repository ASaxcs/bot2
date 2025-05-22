#!/usr/bin/env python3
# processor.py - Modul pemrosesan utama LACIA AI

import os
import json
import torch
from typing import Dict, Any, List, Tuple
from pathlib import Path

class CognitiveProcessor:
    """
    Prosesor kognitif utama yang mengintegrasikan berbagai kemampuan AI
    """
    
    def __init__(self, config):
        """
        Inisialisasi prosesor kognitif
        
        Args:
            config: Konfigurasi sistem
        """
        self.config = config
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Memuat model AI
        self.model = self._load_model()
        
        # Inisialisasi memori
        from lacia_ai.core.cognition.memory.short_term import ShortTermMemory
        from lacia_ai.core.cognition.memory.long_term import LongTermMemory
        
        self.short_term_memory = ShortTermMemory(config.get("memory", {}).get("short_term", {}))
        self.long_term_memory = LongTermMemory(config.get("memory", {}).get("long_term", {}))
        
        # Inisialisasi modul kepribadian
        from lacia_ai.core.personality.emotion.state_manager import EmotionStateManager
        
        self.emotion_manager = EmotionStateManager(config)
        
        # Inisialisasi pengambil keputusan
        from lacia_ai.core.cognition.decision import DecisionEngine
        
        self.decision_engine = DecisionEngine(config)
    
    def _load_model(self):
        """
        Memuat model AI utama dari Hugging Face
        
        Returns:
            Model AI yang dimuat
        """
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            model_path = self.config.get("model", {}).get("path", "mistralai/Mistral-7B-Instruct-v0.2")
            
            print(f"Memuat model {model_path}...")
            
            # Cek jika model tersedia secara lokal atau harus diunduh
            local_path = Path(f"./lacia_ai/models/{os.path.basename(model_path)}")
            
            if local_path.exists() and self.config.get("model", {}).get("use_local", True):
                model_path = str(local_path)
                print(f"Menggunakan model lokal dari {model_path}")
            
            # Konfigurasi untuk perangkat dengan RAM terbatas
            model_config = {
                "device_map": "auto",
                "torch_dtype": torch.float16 if torch.cuda.is_available() else torch.float32,
                "low_cpu_mem_usage": True
            }
            
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = AutoModelForCausalLM.from_pretrained(
                model_path, 
                **model_config
            )
            
            return {"model": model, "tokenizer": tokenizer}
            
        except Exception as e:
            print(f"Error memuat model: {e}")
            print("Menggunakan model dummy sebagai gantinya")
            return {"model": DummyModel(), "tokenizer": DummyTokenizer()}
    
    def process_input(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Memproses input pengguna dan menghasilkan respons
        
        Args:
            user_input: Input teks dari pengguna
            context: Informasi konteks tambahan (opsional)
            
        Returns:
            Dict berisi respons dan informasi pemrosesan
        """
        if context is None:
            context = {}
            
        # Simpan input ke memori jangka pendek
        self.short_term_memory.add_entry({"role": "user", "content": user_input})
        
        # Proses emosi
        emotional_response = self.emotion_manager.get_emotional_response(user_input)
        
        # Dapatkan konteks percakapan
        conversation_history = self.short_term_memory.get_recent_entries(5)
        
        # Format prompt untuk model
        prompt = self._format_prompt(user_input, conversation_history, emotional_response)
        
        # Dapatkan respons dari model
        response = self._get_model_response(prompt)
        
        # Simpan respons ke memori
        self.short_term_memory.add_entry({"role": "assistant", "content": response})
        
        # Evaluasi untuk penyimpanan jangka panjang
        if self.decision_engine.should_store_long_term(user_input, response):
            self.long_term_memory.store_interaction(user_input, response, context)
        
        return {
            "response": response,
            "emotional_state": emotional_response,
            "processing_info": {
                "model_used": self.config.get("model", {}).get("path", "mistral-7b"),
                "device": self.device
            }
        }
    
    def _format_prompt(self, user_input, conversation_history, emotional_state):
        """
        Format prompt untuk model LLM
        
        Args:
            user_input: Input dari pengguna
            conversation_history: Riwayat percakapan terbaru
            emotional_state: Keadaan emosi saat ini
            
        Returns:
            str: Prompt yang diformat
        """
        # Format sederhana untuk model Mistral
        formatted_history = ""
        for entry in conversation_history:
            role = "User" if entry["role"] == "user" else "LACIA"
            formatted_history += f"{role}: {entry['content']}\n\n"
            
        # Tambahkan instruksi emosional jika diperlukan
        dominant_emotion = emotional_state.get("dominant_emotion", "")
        emotion_instruction = ""
        
        if dominant_emotion == "happiness":
            emotion_instruction = "Jawablah dengan nada yang ceria dan antusias."
        elif dominant_emotion == "curiosity":
            emotion_instruction = "Tunjukkan keingintahuan dan dorong eksplorasi."
        elif dominant_emotion == "calmness":
            emotion_instruction = "Berikan respons yang tenang dan terstruktur."
        
        system_prompt = f"""Anda adalah LACIA, asisten AI personal yang cerdas dan bersahabat. 
{emotion_instruction}
"""
        
        full_prompt = f"{system_prompt}\n\n{formatted_history}User: {user_input}\n\nLACIA:"
        
        return full_prompt
    
    def _get_model_response(self, prompt):
        """
        Dapatkan respons dari model LLM
        
        Args:
            prompt: Prompt yang akan diberikan ke model
            
        Returns:
            str: Respons yang dihasilkan
        """
        try:
            model = self.model["model"]
            tokenizer = self.model["tokenizer"]
            
            inputs = tokenizer(prompt, return_tensors="pt").to(self.device)
            
            # Konfigurasi generasi
            gen_config = {
                "max_new_tokens": 512,
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True,
                "pad_token_id": tokenizer.eos_token_id
            }
            
            # Generate respons
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    **gen_config
                )
            
            # Decode dan format respons
            full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Ekstrak hanya bagian respons asisten
            ai_response = full_response.split("LACIA:")[-1].strip()
            
            return ai_response
            
        except Exception as e:
            print(f"Error saat menghasilkan respons: {e}")
            return "Maaf, saya mengalami kesulitan memproses permintaan Anda. Bisakah Anda mencoba lagi?"


# Kelas dummy untuk digunakan jika model gagal dimuat
class DummyModel:
    def generate(self, **kwargs):
        return [torch.tensor([0, 1, 2, 3])]
    
    def to(self, device):
        return self


class DummyTokenizer:
    def __call__(self, text, **kwargs):
        return {"input_ids": torch.tensor([[0, 1, 2, 3]]), "attention_mask": torch.tensor([[1, 1, 1, 1]])}
    
    def decode(self, token_ids, **kwargs):
        return "Saya adalah LACIA. Saat ini saya berjalan dalam mode terbatas karena model utama tidak tersedia. Saya masih dapat membantu dengan pertanyaan dasar."
    
    @property
    def eos_token_id(self):
        return 2
