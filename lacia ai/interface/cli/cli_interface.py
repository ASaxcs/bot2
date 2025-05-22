#!/usr/bin/env python3
# cli_interface.py - Antarmuka Command Line untuk LACIA AI

import os
import sys
import time
import readline
import json
from typing import Dict, Any

# Import modul inti
from lacia_ai.core.cognition.processor import CognitiveProcessor

class CliInterface:
    """
    Implementasi antarmuka command line untuk LACIA AI
    """
    
    def __init__(self, config):
        """
        Inisialisasi antarmuka CLI
        
        Args:
            config: Konfigurasi sistem
        """
        self.config = config
        self.processor = CognitiveProcessor(config)
        self.running = False
        
        # Konfigurasi warna terminal
        self.colors = {
            "reset": "\033[0m",
            "bold": "\033[1m",
            "blue": "\033[34m",
            "green": "\033[32m",
            "cyan": "\033[36m",
            "yellow": "\033[33m",
            "red": "\033[31m",
            "magenta": "\033[35m"
        }
        
        # Cek apakah terminal mendukung warna
        if not sys.stdout.isatty() or os.name == 'nt':
            # Nonaktifkan warna jika tidak didukung
            for key in self.colors:
                self.colors[key] = ""
    
    def start(self):
        """
        Memulai antarmuka command line interaktif
        """
        self.running = True
        self._show_welcome()
        
        try:
            while self.running:
                try:
                    # Dapatkan input pengguna
                    user_input = input(f"{self.colors['green']}Anda: {self.colors['reset']}")
                    
                    # Proses perintah khusus
                    if user_input.lower() in ["/exit", "/quit", "/q"]:
                        print(f"{self.colors['yellow']}Menutup LACIA AI...{self.colors['reset']}")
                        self.running = False
                        break
                    
                    if user_input.lower() in ["/help", "/?"]:
                        self._show_help()
                        continue
                        
                    if user_input.lower() == "/clear":
                        os.system('cls' if os.name == 'nt' else 'clear')
                        continue
                    
                    # Indikator sistem sedang berpikir
                    print(f"{self.colors['cyan']}LACIA sedang berpikir...{self.colors['reset']}")
                    
                    # Proses input dan dapatkan respons
                    start_time = time.time()
                    result = self.processor.process_input(user_input)
                    response_time = time.time() - start_time
                    
                    # Tampilkan respons
                    self._display_response(result, response_time)
                    
                except KeyboardInterrupt:
                    print(f"\n{self.colors['yellow']}Operasi dibatalkan.{self.colors['reset']}")
                except EOFError:
                    print(f"\n{self.colors['yellow']}Menutup LACIA AI...{self.colors['reset']}")
                    self.running = False
                    break
                
        except Exception as e:
            print(f"{self.colors['red']}Error: {e}{self.colors['reset']}")
            
        finally:
            print(f"{self.colors['magenta']}Terima kasih telah menggunakan LACIA AI!{self.colors['reset']}")
    
    def _show_welcome(self):
        """Menampilkan pesan selamat datang"""
        lacia_art = f"""
{self.colors['cyan']}
    __    ___   ____ ___   ___ 
   / /   /   | / __//   / /   |
  / /   / /| |/ / //   / / /| |
 / /___/ ___ / / //   / / ___ |
/_____/_/  |_____/___/_/_/  |_|
{self.colors['reset']}
{self.colors['bold']}LACIA AI - Asisten AI Personal{self.colors['reset']}
Versi 0.1.0
Tulis {self.colors['yellow']}/help{self.colors['reset']} untuk informasi penggunaan
Tulis {self.colors['yellow']}/exit{self.colors['reset']} untuk keluar
"""
        print(lacia_art)
    
    def _show_help(self):
        """Menampilkan bantuan penggunaan"""
        help_text = f"""
{self.colors['bold']}Perintah yang Tersedia:{self.colors['reset']}
  {self.colors['yellow']}/help{self.colors['reset']}  - Menampilkan bantuan ini
  {self.colors['yellow']}/exit{self.colors['reset']}  - Keluar dari LACIA AI
  {self.colors['yellow']}/quit{self.colors['reset']}  - Alias untuk /exit
  {self.colors['yellow']}/clear{self.colors['reset']} - Membersihkan layar terminal

{self.colors['bold']}Fitur Utama:{self.colors['reset']}
  - Percakapan natural dengan model Mistral-7B
  - Memori jangka pendek dan panjang
  - Adaptasi kepribadian dinamis

{self.colors['bold']}Catatan:{self.colors['reset']}
  - Gunakan bahasa alami untuk berkomunikasi dengan LACIA
  - LACIA dapat mengingat konteks percakapan dalam satu sesi
  - Untuk informasi teknis dan kemajuan pemrosesan, gunakan mode debug
"""
        print(help_text)
    
    def _display_response(self, result: Dict[str, Any], response_time: float):
        """
        Menampilkan respons AI dengan format yang baik
        
        Args:
            result: Hasil pemrosesan
            response_time: Waktu pemrosesan dalam detik
        """
        response = result.get("response", "")
        emotional_state = result.get("emotional_state", {})
        
        # Tampilkan respons utama
        print(f"\n{self.colors['magenta']}LACIA: {self.colors['reset']}{response}\n")
        
        # Tampilkan informasi debug jika diaktifkan
        if self.config.get("interface", {}).get("debug_mode", False):
            print(f"{self.colors['yellow']}--- Info Debug ---{self.colors['reset']}")
            print(f"Waktu respons: {response_time:.2f} detik")
            print(f"Emosi dominan: {emotional_state.get('dominant_emotion', 'netral')}")
            print(f"Model: {result.get('processing_info', {}).get('model_used', 'unknown')}")
            print(f"Perangkat: {result.get('processing_info', {}).get('device', 'unknown')}")
            print(f"{self.colors['yellow']}----------------{self.colors['reset']}\n")
