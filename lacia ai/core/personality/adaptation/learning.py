#!/usr/bin/env python3
# learning.py - Implementasi sistem adaptasi dan pembelajaran LACIA AI

from typing import Dict, List, Any, Tuple
import json
import os
import time
import random

class Learning:
    """
    Kelas yang mengimplementasikan kemampuan adaptasi dan pembelajaran
    pada LACIA AI berdasarkan interaksi dengan pengguna dan lingkungan.
    """
    
    def __init__(self, learning_config_path: str = None, user_profile_path: str = None):
        """
        Inisialisasi sistem pembelajaran
        
        Args:
            learning_config_path: Path ke file konfigurasi pembelajaran
            user_profile_path: Path ke file profil pengguna
        """
        self.config = self._load_learning_config(learning_config_path)
        self.user_profile = self._load_user_profile(user_profile_path)
        self.learning_history = []
        self.response_effectiveness = {}  # Efektivitas jenis respons
        self.topics_of_interest = {}      # Topik yang menarik bagi pengguna
        self.behavioral_adjustments = {}  # Penyesuaian perilaku
        self.max_history_length = 100
        
    def _load_learning_config(self, config_path: str = None) -> Dict[str, Any]:
        """
        Memuat konfigurasi pembelajaran dari file atau menggunakan konfigurasi default
        
        Args:
            config_path: Path ke file konfigurasi
            
        Returns:
            Konfigurasi pembelajaran berupa dictionary
        """
        default_config = {
            "learning_rate": 0.1,        # Kecepatan penyesuaian
            "memory_retention": 0.95,    # Retensi memori (faktor peluruhan)
            "exploration_rate": 0.2,     # Tingkat eksplorasi untuk mencoba respons baru
            "reinforcement_factor": 0.3, # Faktor penguatan untuk feedback positif
            "inhibition_factor": 0.2,    # Faktor penghambatan untuk feedback negatif
            "adaptation_settings": {
                "response_style": True,   # Adaptasi gaya respons
                "conversation_depth": True, # Adaptasi kedalaman percakapan
                "topic_selection": True,  # Adaptasi pemilihan topik
                "emotional_tone": True    # Adaptasi nada emosional
            },
            "learning_thresholds": {
                "min_interactions": 5,    # Interaksi minimum sebelum beradaptasi
                "confidence_threshold": 0.6 # Ambang batas kepercayaan untuk menerapkan pembelajaran
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading learning config: {e}")
                return default_config
        else:
            return default_config
    
    def _load_user_profile(self, profile_path: str = None) -> Dict[str, Any]:
        """
        Memuat profil pengguna dari file atau membuat profil kosong
        
        Args:
            profile_path: Path ke file profil
            
        Returns:
            Profil pengguna berupa dictionary
        """
        empty_profile = {
            "interaction_count": 0,
            "first_interaction": time.time(),
            "last_interaction": time.time(),
            "interests": {},
            "preferred_response_styles": {},
            "preferred_conversation_depth": "medium",
            "feedback_history": [],
            "session_stats": {}
        }
        
        if profile_path and os.path.exists(profile_path):
            try:
                with open(profile_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading user profile: {e}")
                return empty_profile
        else:
            return empty_profile
    
    def save_user_profile(self, profile_path: str) -> bool:
        """
        Menyimpan profil pengguna ke file
        
        Args:
            profile_path: Path ke file tujuan
            
        Returns:
            True jika berhasil, False jika gagal
        """
        try:
            # Perbarui waktu interaksi terakhir
            self.user_profile["last_interaction"] = time.time()
            
            # Pastikan direktori ada
            os.makedirs(os.path.dirname(profile_path), exist_ok=True)
            
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(self.user_profile, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving user profile: {e}")
            return False
    
    def record_interaction(self, user_input: str, ai_response: str, 
                         context_data: Dict[str, Any]) -> None:
        """
        Mencatat interaksi untuk pembelajaran
        
        Args:
            user_input: Input dari pengguna
            ai_response: Respons dari AI
            context_data: Data konteks interaksi
        """
        # Perbarui jumlah interaksi
        self.user_profile["interaction_count"] += 1
        
        # Catat waktu interaksi
        timestamp = time.time()
        
        # Tambahkan ke riwayat pembelajaran
        interaction_record = {
            "timestamp": timestamp,
            "user_input": user_input,
            "ai_response": ai_response,
            "context": context_data,
            "feedback": None  # Akan diisi nanti jika ada feedback
        }
        self.learning_history.append(interaction_record)
        
        # Batasi ukuran riwayat
        if len(self.learning_history) > self.max_history_length:
            self.learning_history.pop(0)
            
        # Identifikasi dan catat topik dari input
        topics = context_data.get("identified_topics", [])
        for topic in topics:
            if topic in self.topics_of_interest:
                self.topics_of_interest[topic] += 1
            else:
                self.topics_of_interest[topic] = 1
                
            # Perbarui minat di profil pengguna
            if topic in self.user_profile["interests"]:
                self.user_profile["interests"][topic] += 1
            else:
                self.user_profile["interests"][topic] = 1
    
    def process_user_feedback(self, feedback_type: str, feedback_strength: float,
                           interaction_index: int = -1) -> None:
        """
        Memproses umpan balik dari pengguna untuk penyesuaian pembelajaran
        
        Args:
            feedback_type: Jenis umpan balik ('positive', 'negative', 'neutral')
            feedback_strength: Kekuatan umpan balik (0-1)
            interaction_index: Indeks interaksi yang diberi umpan balik (-1 untuk terakhir)
        """
        if not self.learning_history:
            return
            
        # Pastikan indeks valid
        if interaction_index < 0:
            interaction_index = len(self.learning_history) + interaction_index
            
        if interaction_index < 0 or interaction_index >= len(self.learning_history):
            return
            
        # Ambil interaksi yang sesuai
        interaction = self.learning_history[interaction_index]
        
        # Catat umpan balik
        interaction["feedback"] = {
            "type": feedback_type,
            "strength": feedback_strength,
            "timestamp": time.time()
        }
        
        # Catat ke riwayat umpan balik pengguna
        self.user_profile["feedback_history"].append({
            "type": feedback_type,
            "strength": feedback_strength,
            "timestamp": time.time(),
            "response_type": interaction.get("context", {}).get("response_type", "unknown")
        })
        
        # Sesuaikan efektivitas jenis respons
        response_type = interaction.get("context", {}).get("response_type", "unknown")
        
        if response_type not in self.response_effectiveness:
            self.response_effectiveness[response_type] = 0.5  # Nilai awal netral
            
        # Faktor penyesuaian berdasarkan jenis umpan balik
        adjustment = 0
        learning_rate = self.config.get("learning_rate", 0.1)
        
        if feedback_type == "positive":
            adjustment = learning_rate * self.config.get("reinforcement_factor", 0.3) * feedback_strength
        elif feedback_type == "negative":
            adjustment = -learning_rate * self.config.get("inhibition_factor", 0.2) * feedback_strength
            
        # Terapkan penyesuaian
        self.response_effectiveness[response_type] += adjustment
        
        # Pastikan nilai tetap dalam rentang 0-1
        self.response_effectiveness[response_type] = max(0.0, min(1.0, self.response_effectiveness[response_type]))
        
        # Perbarui gaya respons yang disukai dalam profil pengguna
        if response_type in self.user_profile["preferred_response_styles"]:
            self.user_profile["preferred_response_styles"][response_type] += adjustment
        else:
            self.user_profile["preferred_response_styles"][response_type] = 0.5 + adjustment
            
        # Pastikan nilai tetap dalam rentang 0-1
        self.user_profile["preferred_response_styles"][response_type] = max(0.0, min(1.0, 
            self.user_profile["preferred_response_styles"][response_type]))
    
    def adapt_response_strategy(self, available_strategies: List[str], 
                             context_data: Dict[str, Any]) -> str:
        """
        Menyesuaikan strategi respons berdasarkan pembelajaran
        
        Args:
            available_strategies: Daftar strategi yang tersedia
            context_data: Data konteks untuk keputusan
            
        Returns:
            Strategi respons yang dipilih
        """
        # Jika tidak ada strategi tersedia, kembalikan kosong
        if not available_strategies:
            return ""
            
        # Jika belum cukup interaksi, pilih secara acak
        min_interactions = self.config.get("learning_thresholds", {}).get("min_interactions", 5)
        
        if self.user_profile["interaction_count"] < min_interactions:
            return random.choice(available_strategies)
            
        # Periksa pengaturan adaptasi
        if not self.config.get("adaptation_settings", {}).get("response_style", True):
            return random.choice(available_strategies)
            
        # Bangun daftar strategi dengan bobot efektivitas
        weighted_strategies = []
        
        for strategy in available_strategies:
            # Dapatkan efektivitas atau default jika tidak ada
            effectiveness = self.response_effectiveness.get(strategy, 0.5)
            
            # Tambahkan eksplorasi untuk strategi yang belum sering digunakan
            exploration_factor = self.config.get("exploration_rate", 0.2)
            
            if strategy not in self.response_effectiveness:
                effectiveness += exploration_factor
                
            weighted_strategies.append((strategy, effectiveness))
            
        # Urutkan berdasarkan efektivitas
        weighted_strategies.sort(key=lambda x: x[1], reverse=True)
        
        # Pilih strategi terbaik tetapi kadang-kadang eksplorasi strategi baru
        if random.random() < self.config.get("exploration_rate", 0.2):
            # Eksplorasi: pilih strategi secara acak
            return random.choice(available_strategies)
        else:
            # Eksploitasi: pilih strategi terbaik
            return weighted_strategies[0][0] if weighted_strategies else random.choice(available_strategies)
    
    def get_preferred_depth(self) -> str:
        """
        Mendapatkan kedalaman percakapan yang disukai pengguna
        
        Returns:
            Tingkat kedalaman ('shallow', 'medium', 'deep')
        """
        return self.user_profile.get("preferred_conversation_depth", "medium")
    
    def adjust_conversation_depth(self, current_depth: str, user_engagement: float) -> str:
        """
        Menyesuaikan kedalaman percakapan berdasarkan keterlibatan pengguna
        
        Args:
            current_depth: Kedalaman saat ini ('shallow', 'medium', 'deep')
            user_engagement: Tingkat keterlibatan pengguna (0-1)
            
        Returns:
            Kedalaman percakapan yang disesuaikan
        """
        # Periksa pengaturan adaptasi
        if not self.config.get("adaptation_settings", {}).get("conversation_depth", True):
            return current_depth
            
        depth_levels = ["shallow", "medium", "deep"]
        
        try:
            current_index = depth_levels.index(current_depth)
        except ValueError:
            current_index = 1  # Default ke 'medium'
            
        # Sesuaikan berdasarkan keterlibatan
        if user_engagement > 0.7 and current_index < 2:
            # Pengguna sangat terlibat, tingkatkan kedalaman
            new_index = current_index + 1
        elif user_engagement < 0.3 and current_index > 0:
            # Pengguna kurang terlibat, kurangi kedalaman
            new_index = current_index - 1
        else:
            # Pertahankan kedalaman saat ini
            new_index = current_index
            
        # Perbarui kedalaman percakapan yang disukai di profil pengguna
        self.user_profile["preferred_conversation_depth"] = depth_levels[new_index]
        
        return depth_levels[new_index]
    
    def identify_topics_of_interest(self, user_message: str, 
                                  identified_topics: List[str]) -> List[Tuple[str, float]]:
        """
        Mengidentifikasi topik yang menarik bagi pengguna berdasarkan riwayat interaksi
        
        Args:
            user_message: Pesan dari pengguna
            identified_topics: Daftar topik yang diidentifikasi dari pesan
            
        Returns:
            Daftar topik dengan skor minat (topik, skor)
        """
        # Jika tidak ada topik diidentifikasi, kembalikan daftar kosong
        if not identified_topics:
            return []
            
        # Bangun daftar topik dengan skor minat
        topic_scores = []
        
        for topic in identified_topics:
            # Dapatkan frekuensi topik dari riwayat
            frequency = self.topics_of_interest.get(topic, 0)
            
            # Dapatkan minat dari profil pengguna
            interest_level = self.user_profile["interests"].get(topic, 0)
            
            # Hitung skor minat (kombinasi frekuensi dan minat)
            interest_score = 0.4 * frequency + 0.6 * interest_level
            
            # Normalisasi skor (opsional)
            normalized_score = min(1.0, interest_score / 10.0)
            
            topic_scores.append((topic, normalized_score))
            
        # Urutkan berdasarkan skor minat
        topic_scores.sort(key=lambda x: x[1], reverse=True)
        
        return topic_scores
    
    def suggest_topics(self, current_context: Dict[str, Any], 
                     max_suggestions: int = 3) -> List[str]:
        """
        Menyarankan topik berdasarkan minat pengguna
        
        Args:
            current_context: Konteks percakapan saat ini
            max_suggestions: Jumlah maksimum saran
            
        Returns:
            Daftar topik yang disarankan
        """
        # Periksa pengaturan adaptasi
        if not self.config.get("adaptation_settings", {}).get("topic_selection", True):
            return []
            
        # Dapatkan topik dengan minat tertinggi
        all_topics = list(self.user_profile["interests"].items())
        
        # Urutkan berdasarkan minat
        all_topics.sort(key=lambda x: x[1], reverse=True)
        
        # Filter topik yang relevan dengan konteks saat ini (implementasi sederhana)
        relevant_topics = []
        
        current_topic = current_context.get("current_topic", "")
        
        for topic, interest in all_topics:
            # Hindari mengulang topik saat ini
            if topic == current_topic:
                continue
                
            # Implementasi logika relevansi di sini
            # Contoh sederhana: topik yang memiliki skor minat tinggi
            if interest > 5:
                relevant_topics.append(topic)
                
        # Batasi jumlah saran
        return relevant_topics[:max_suggestions]
    
    def adjust_emotional_tone(self, user_emotion: str, 
                           conversation_history: List[Dict]) -> str:
        """
        Menyesuaikan nada emosional respons berdasarkan emosi pengguna
        
        Args:
            user_emotion: Emosi yang terdeteksi dari pengguna
            conversation_history: Riwayat percakapan terbaru
            
        Returns:
            Nada emosional yang disarankan ('neutral', 'empathetic', 'cheerful', dsb)
        """
        # Periksa pengaturan adaptasi
        if not self.config.get("adaptation_settings", {}).get("emotional_tone", True):
            return "neutral"
        
        # Pemetaan sederhana dari emosi pengguna ke nada respons
        emotion_tone_map = {
            "happy": "cheerful",
            "sad": "empathetic",
            "angry": "calm",
            "confused": "helpful",
            "frustrated": "supportive",
            "neutral": "neutral",
            "excited": "enthusiastic"
        }
        
        # Default ke nada netral jika emosi tidak dikenali
        suggested_tone = emotion_tone_map.get(user_emotion, "neutral")
        
        # Analisis percakapan terakhir untuk konsistensi nada
        if conversation_history and len(conversation_history) >= 3:
            # Jika ada perubahan emosi yang signifikan, sesuaikan nada secara bertahap
            # Logika implementasi di sini
            pass
            
        return suggested_tone
    
    def analyze_response_effectiveness(self, time_period: str = "week") -> Dict[str, Any]:
        """
        Menganalisis efektivitas respons dalam periode waktu tertentu
        
        Args:
            time_period: Periode waktu untuk analisis ('day', 'week', 'month')
            
        Returns:
            Hasil analisis berupa dictionary
        """
        now = time.time()
        
        # Tentukan batas waktu berdasarkan periode
        if time_period == "day":
            time_limit = now - (24 * 60 * 60)
        elif time_period == "week":
            time_limit = now - (7 * 24 * 60 * 60)
        elif time_period == "month":
            time_limit = now - (30 * 24 * 60 * 60)
        else:
            time_limit = 0  # Analisis semua data
            
        # Filter umpan balik dalam periode waktu
        recent_feedback = [
            feedback for feedback in self.user_profile["feedback_history"]
            if feedback["timestamp"] >= time_limit
        ]
        
        if not recent_feedback:
            return {"status": "insufficient_data"}
            
        # Hitung statistik
        response_types = {}
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for feedback in recent_feedback:
            feedback_type = feedback["type"]
            response_type = feedback["response_type"]
            
            # Hitung berdasarkan jenis umpan balik
            if feedback_type == "positive":
                positive_count += 1
            elif feedback_type == "negative":
                negative_count += 1
            else:
                neutral_count += 1
                
            # Hitung berdasarkan jenis respons
            if response_type not in response_types:
                response_types[response_type] = {
                    "positive": 0,
                    "negative": 0,
                    "neutral": 0,
                    "total": 0
                }
                
            response_types[response_type][feedback_type] += 1
            response_types[response_type]["total"] += 1
            
        # Hitung efektivitas untuk setiap jenis respons
        for response_type, counts in response_types.items():
            total = counts["total"]
            if total > 0:
                effectiveness = (counts["positive"] - counts["negative"]) / total
                response_types[response_type]["effectiveness"] = min(1.0, max(-1.0, effectiveness))
                
        # Buat hasil analisis
        total_feedback = positive_count + negative_count + neutral_count
        
        analysis_result = {
            "period": time_period,
            "total_feedback": total_feedback,
            "positive_rate": positive_count / total_feedback if total_feedback > 0 else 0,
            "negative_rate": negative_count / total_feedback if total_feedback > 0 else 0,
            "neutral_rate": neutral_count / total_feedback if total_feedback > 0 else 0,
            "response_types": response_types,
            "most_effective": max(response_types.items(), key=lambda x: x[1].get("effectiveness", -1))[0] 
                            if response_types else None,
            "least_effective": min(response_types.items(), key=lambda x: x[1].get("effectiveness", 1))[0]
                            if response_types else None
        }
        
        return analysis_result
    
    def update_learning_parameters(self) -> None:
        """
        Memperbarui parameter pembelajaran berdasarkan analisis kinerja
        """
        # Analisis efektivitas terkini
        effectiveness_analysis = self.analyze_response_effectiveness("week")
        
        # Jika data tidak cukup, tidak perlu memperbarui
        if effectiveness_analysis.get("status") == "insufficient_data":
            return
            
        # Sesuaikan tingkat eksplorasi berdasarkan tingkat negatif
        negative_rate = effectiveness_analysis.get("negative_rate", 0)
        
        if negative_rate > 0.4:
            # Tingkat negatif tinggi, tingkatkan eksplorasi
            self.config["exploration_rate"] = min(0.5, self.config["exploration_rate"] * 1.2)
        elif negative_rate < 0.2:
            # Tingkat negatif rendah, kurangi eksplorasi
            self.config["exploration_rate"] = max(0.1, self.config["exploration_rate"] * 0.9)
            
        # Sesuaikan tingkat pembelajaran
        if self.user_profile["interaction_count"] > 100:
            # Pengguna berpengalaman, kurangi tingkat pembelajaran
            self.config["learning_rate"] = max(0.05, self.config["learning_rate"] * 0.95)
    
    def decay_old_learning(self) -> None:
        """
        Menerapkan peluruhan pada pembelajaran lama untuk memberi bobot lebih pada
        pengalaman terbaru
        """
        decay_factor = self.config.get("memory_retention", 0.95)
        
        # Terapkan peluruhan pada minat topik
        for topic in self.topics_of_interest:
            self.topics_of_interest[topic] *= decay_factor
            
            # Hapus topik dengan nilai sangat rendah
            if self.topics_of_interest[topic] < 0.1:
                self.topics_of_interest[topic] = 0
                
        # Terapkan peluruhan pada efektivitas respons
        for response_type in self.response_effectiveness:
            # Peluruhan mendekati nilai netral (0.5)
            diff_from_neutral = self.response_effectiveness[response_type] - 0.5
            self.response_effectiveness[response_type] = 0.5 + diff_from_neutral * decay_factor
    
    def get_personalization_report(self) -> Dict[str, Any]:
        """
        Menghasilkan laporan personalisasi tentang adaptasi sistem
        
        Returns:
            Laporan personalisasi berupa dictionary
        """
        # Daftar topik dengan minat tertinggi
        top_interests = list(self.user_profile["interests"].items())
        top_interests.sort(key=lambda x: x[1], reverse=True)
        top_interests = top_interests[:5]  # 5 teratas
        
        # Daftar strategi respons efektif
        effective_strategies = list(self.response_effectiveness.items())
        effective_strategies.sort(key=lambda x: x[1], reverse=True)
        
        # Buat laporan
        report = {
            "user_stats": {
                "interaction_count": self.user_profile["interaction_count"],
                "first_interaction": self.user_profile["first_interaction"],
                "last_interaction": self.user_profile["last_interaction"],
                "days_active": (self.user_profile["last_interaction"] - 
                              self.user_profile["first_interaction"]) / (24 * 60 * 60)
            },
            "personalization": {
                "top_interests": top_interests,
                "preferred_depth": self.user_profile["preferred_conversation_depth"],
                "effective_response_types": effective_strategies,
                "learning_status": "active" if self.user_profile["interaction_count"] >= 
                                 self.config["learning_thresholds"]["min_interactions"] else "gathering_data"
            },
            "adaptation_settings": self.config["adaptation_settings"]
        }
        
        return report
    
    def reset_learning(self, reset_type: str = "full") -> None:
        """
        Mengembalikan sistem pembelajaran ke kondisi awal
        
        Args:
            reset_type: Jenis reset ('full', 'preferences', 'history')
        """
        if reset_type == "full" or reset_type == "history":
            self.learning_history = []
            
        if reset_type == "full" or reset_type == "preferences":
            self.response_effectiveness = {}
            self.topics_of_interest = {}
            self.behavioral_adjustments = {}
            
        if reset_type == "full":
            # Reset profil pengguna ke kondisi awal tetapi pertahankan informasi dasar
            self.user_profile = {
                "interaction_count": 0,
                "first_interaction": time.time(),
                "last_interaction": time.time(),
                "interests": {},
                "preferred_response_styles": {},
                "preferred_conversation_depth": "medium",
                "feedback_history": [],
                "session_stats": {}
            }
            
# Contoh penggunaan:
if __name__ == "__main__":
    # Inisialisasi sistem pembelajaran
    learning_system = Learning()
    
    # Simulasi interaksi
    user_input = "Bagaimana cara kerja quantum computing?"
    ai_response = "Quantum computing menggunakan prinsip mekanika kuantum seperti superposisi..."
    context = {
        "identified_topics": ["quantum computing", "technology", "physics"],
        "response_type": "educational"
    }
    
    # Catat interaksi
    learning_system.record_interaction(user_input, ai_response, context)
    
    # Simulasi umpan balik positif
    learning_system.process_user_feedback("positive", 0.8)
    
    # Dapatkan strategi adaptasi untuk respons berikutnya
    strategies = ["educational", "conversational", "concise", "detailed"]
    selected_strategy = learning_system.adapt_response_strategy(strategies, {})
    
    print(f"Strategi terpilih: {selected_strategy}")
    
    # Dapatkan laporan personalisasi
    report = learning_system.get_personalization_report()
    print(f"Top interests: {report['personalization']['top_interests']}")