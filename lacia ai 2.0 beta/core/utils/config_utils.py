"""
Configuration utilities for safe config loading
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Union

def safe_load_config(config_path: Union[str, dict, Path]) -> Dict[str, Any]:
    """Safely load configuration with proper validation"""
    
    # If already a dict, return it
    if isinstance(config_path, dict):
        print(f"Warning: Config path is dict, using provided config")
        return config_path
    
    # Validate path type
    if not isinstance(config_path, (str, Path)):
        print(f"Warning: Invalid config path type: {type(config_path)}")
        return {}
    
    config_path = Path(config_path)
    
    try:
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"Warning: Config file not found: {config_path}")
            return {}
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {e}")
        return {}
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def validate_config_structure(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and fix common config structure issues"""
    
    # Ensure required sections exist
    required_sections = ['data', 'cognition', 'personality', 'emotion', 'output_formatting']
    
    for section in required_sections:
        if section not in config:
            config[section] = {}
    
    # Fix common path issues
    data_section = config.get('data', {})
    if 'experiences_path' not in data_section:
        data_section['experiences_path'] = 'data/experiences.json'
    
    if 'triggers_config' not in data_section:
        data_section['triggers_config'] = 'config/triggers.json'
    
    if 'tasks_config' not in data_section:
        data_section['tasks_config'] = 'config/tasks.json'
    
    return config
