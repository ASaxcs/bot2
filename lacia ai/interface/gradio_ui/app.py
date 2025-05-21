#!/usr/bin/env python3
# app.py - File Utama untuk LACIA AI

import os
import sys
import argparse
from lacia_ai.interfaces.cli import cli_interface
from lacia_ai.core.cognition.processor import InputProcessor
from lacia_ai.system.config_manager import ConfigManager

def main():
    """
    Fungsi utama untuk menjalankan LACIA AI
    """
    parser = argparse.ArgumentParser(description="LACIA AI - Asisten AI Personal")
    parser.add_argument('--mode', type=str, default='cli', 
                        choices=['cli', 'web', 'api'],
                        help='Mode antarmuka (cli, web, atau api)')
    parser.add_argument('--debug', action='store_true',
                        help='Aktifkan mode debug')
    
    args = parser.parse_args()
    
    # Inisialisasi konfigurasi
    config = ConfigManager()
    config.load_config()
    
    # Setel mode debug jika diminta
    if args.debug:
        config.set('system', 'debug_mode', True)
        print("Mode debug diaktifkan")
    
    # Jalankan antarmuka yang sesuai
    if args.mode == 'cli':
        print("Memulai LACIA AI dalam mode CLI...")
        cli_interface.start()
    elif args.mode == 'web':
        try:
            from lacia_ai.interfaces.gradio_ui import app as web_app
            print("Memulai LACIA AI dalam mode web...")
            web_app.start()
        except ImportError:
            print("Error: Modul gradio belum diinstal. Gunakan 'pip install gradio' untuk meng