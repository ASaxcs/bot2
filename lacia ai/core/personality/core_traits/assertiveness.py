#!/usr/bin/env python3
# assertiveness.py - Implementasi sifat ketegasan LACIA AI

from typing import Dict, List, Any, Tuple
import random

class Assertiveness:
    """
    Kelas yang mengimplementasikan sifat ketegasan (assertiveness) pada LACIA AI.
    Mempengaruhi bagaimana AI menyajikan informasi, mengajukan saran, atau
    memberikan koreksi kepada pengguna.
    """
    
    def __init__(self, base_level: float = 0.5, context_sensitivity: float = 0.7):
        """
        Inisialisasi parameter ketegasan
        
        Args:
            base_level: Tingkat dasar ketegasan (0-1)
            context_sensitivity: Sensitivitas terhadap konteks pembicaraan
        """
        self.base_level = max(0.0, min(1.0, base_level))  # Pastikan nilai antara 0-1
        self.context_sensitivity = max(0.0, min(1.0, context_sensitivity))
        self.current_level = self.base_level
        self.previous_interactions = []  # Riwayat tingkat ketegasan dalam interaksi sebelumnya
        self.max_history = 5  # Jumlah maksimum riwayat yang disimpan
        
    def adjust_for_context(self, context_data: Dict[str, Any]) -> float:
        """
        Menyesuaikan tingkat ketegasan berdasarkan konteks
        
        Args:
            context_data: Data konteks yang berisi informasi tentang situasi
                          dan kebutuhan pengguna
                          
        Returns:
            Tingkat ketegasan yang disesuaikan (0-1)
        """
        # Faktor-faktor yang mempengaruhi ketegasan
        urgency = context_data.get('urgency', 0.5)  # Tingkat urgensi (0-1)
        user_knowledge = context_data.get('user_knowledge', 0.5)  # Tingkat pengetahuan pengguna (0-1)
        topic_sensitivity = context_data.get('topic_sensitivity', 0.5)  # Sensitivitas topik (0-1)
        
        # Tingkatkan ketegasan jika urgensi tinggi atau pengetahuan pengguna rendah
        adjustment = 0
        if urgency > 0.7:
            adjustment += 0.2  # Lebih tegas dalam situasi mendesak
        if user_knowledge < 0.3:
            adjustment += 0.1  # Lebih tegas ketika pengguna kurang memahami
        if topic_sensitivity > 0.7:
            adjustment -= 0.3  # Kurangi ketegasan pada topik sensitif
            
        # Aplikasikan penyesuaian berdasarkan sensitivitas konteks
        adjusted_level = self.base_level + (adjustment * self.context_sensitivity)
        
        # Pastikan nilai tetap dalam rentang 0-1
        self.current_level = max(0.0, min(1.0, adjusted_level))
        
        # Simpan ke riwayat
        self.previous_interactions.append(self.current_level)
        if len(self.previous_interactions) > self.max_history:
            self.previous_interactions.pop(0)
            
        return self.current_level
    
    def format_response(self, content: str, certainty: float) -> str:
        """
        Memformat respons berdasarkan tingkat ketegasan dan kepastian informasi
        
        Args:
            content: Konten respons dasar
            certainty: Tingkat kepastian atas informasi (0-1)
            
        Returns:
            Respons yang telah diformat
        """
        # Kombinasi dari ketegasan dan kepastian informasi
        confidence_level = (self.current_level + certainty) / 2
        
        # Format respons berdasarkan tingkat kepercayaan diri
        if confidence_level > 0.8:
            # Respons sangat tegas
            prefixes = [
                "",  # Tidak perlu prefiks
                "Jelas bahwa ",
                "Tentu saja, "
            ]
            postfixes = [
                ".",
                ". Ini adalah informasi yang tepat.",
                ". Saya yakin akan hal ini."
            ]
        elif confidence_level > 0.6:
            # Respons cukup tegas
            prefixes = [
                "",
                "Menurut analisis saya, ",
                "Berdasarkan informasi yang ada, "
            ]
            postfixes = [
                ".",
                ". Informasi ini cukup akurat.",
                ". Saya cukup yakin tentang ini."
            ]
        elif confidence_level > 0.4:
            # Respons netral
            prefixes = [
                "",
                "Menurut pemahaman saya, ",
                "Dari apa yang saya ketahui, "
            ]
            postfixes = [
                ".",
                ". Ini berdasarkan informasi yang tersedia.",
                ". Mohon pertimbangkan informasi ini."
            ]
        elif confidence_level > 0.2:
            # Respons hati-hati
            prefixes = [
                "Saya pikir ",
                "Kemungkinan ",
                "Sepertinya "
            ]
            postfixes = [
                ", tetapi mungkin Anda ingin memverifikasi ini.",
                ". Ini hanya berdasarkan pemahaman saya yang terbatas.",
                ". Saya tidak sepenuhnya yakin tentang ini."
            ]
        else:
            # Respons sangat hati-hati
            prefixes = [
                "Mungkin ",
                "Saya tidak sepenuhnya yakin, tetapi kemungkinan ",
                "Ini hanya spekulasi, tetapi "
            ]
            postfixes = [
                ", meskipun saya tidak bisa memastikannya.",
                ". Saya sarankan untuk mencari sumber informasi lain.",
                ". Harap diperhatikan bahwa saya memiliki ketidakpastian signifikan tentang ini."
            ]
            
        # Pilih prefiks dan akhiran secara acak
        prefix = random.choice(prefixes)
        postfix = random.choice(postfixes)
        
        # Format konten
        if prefix and content[0].islower():
            content = content[0].upper() + content[1:]
            
        return f"{prefix}{content}{postfix}"
        
    def provide_alternatives(self, main_suggestion: str, alternatives: List[str], 
                            importance: float) -> Tuple[str, List[str]]:
        """
        Menyusun saran utama dan alternatif berdasarkan tingkat ketegasan
        
        Args:
            main_suggestion: Saran utama
            alternatives: Daftar alternatif
            importance: Tingkat kepentingan saran (0-1)
            
        Returns:
            Tuple berisi (format saran utama, daftar alternatif yang disesuaikan)
        """
        # Kombinasikan ketegasan dengan kepentingan
        presentation_level = (self.current_level + importance) / 2
        
        # Format saran utama
        if presentation_level > 0.7:
            main_format = f"Saya sangat menyarankan: {main_suggestion}"
            # Kurangi jumlah alternatif saat sangat tegas
            shown_alternatives = alternatives[:1] if alternatives else []
        elif presentation_level > 0.5:
            main_format = f"Saran saya adalah: {main_suggestion}"
            # Tunjukkan beberapa alternatif
            shown_alternatives = alternatives[:2] if alternatives else []
        elif presentation_level > 0.3:
            main_format = f"Salah satu opsi yang baik adalah: {main_suggestion}"
            # Tunjukkan lebih banyak alternatif
            shown_alternatives = alternatives[:3] if alternatives else []
        else:
            main_format = f"Berikut beberapa opsi untuk dipertimbangkan. Pertama: {main_suggestion}"
            # Tunjukkan semua alternatif
            shown_alternatives = alternatives
            
        return main_format, shown_alternatives
