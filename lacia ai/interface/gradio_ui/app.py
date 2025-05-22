#!/usr/bin/env python3
# app.py - File utama aplikasi LACIA AI

import os
import argparse
from lacia_ai.interfaces.cli.cli_interface import CliInterface
from lacia_ai.system.config_manager import ConfigManager

def main():
    """
    Fungsi utama untuk menjalankan LACIA AI
    """
    parser = argparse.ArgumentParser(description='LACIA AI - Asisten AI Personal')
    parser.add_argument('--interface', type=str, default='cli', 
                      choices=['cli', 'web', 'api'],
                      help='Pilih antarmuka (cli, web, atau api)')
    parser.add_argument('--config', type=str, default='default',
                      help='Gunakan file konfigurasi tertentu')
    args = parser.parse_args()
    
    # Inisialisasi konfigurasi
    config = ConfigManager(args.config)
    
    # Jalankan interface yang sesuai
    if args.interface == 'cli':
        interface = CliInterface(config)
        interface.start()
    elif args.interface == 'web':
        from lacia_ai.interfaces.gradio_ui.app import WebInterface
        interface = WebInterface(config)
        interface.start()
    elif args.interface == 'api':
        from lacia_ai.interfaces.api.fastapi_app import ApiInterface
        interface = ApiInterface(config)
        interface.start()

if __name__ == "__main__":
    main()