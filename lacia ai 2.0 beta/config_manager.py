"""
Configuration Manager for Lacia AI
Handles loading, saving, and managing system configuration
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

class ConfigManager:
    """Manages system configuration with validation and defaults"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.logger = logging.getLogger(__name__)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration with fallback to defaults"""
        default_config = self._get_default_config()
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    default_config.update(loaded_config)
                    self._validate_config(default_config)
            except Exception as e:
                print(f"Error loading config: {e}, using defaults")
        else:
            # Create default config file
            self.save_config(default_config)
        
        return default_config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "model": {
                "model_id": "TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
                "model_basename": "mistral-7b-instruct-v0.2.Q4_K_M.gguf",
                "model_path": "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
                "n_ctx": 2048,
                "n_batch": 512,
                "n_threads": None,
                "max_tokens": 512,
                "temperature": 0.7,
                "top_p": 0.9,
                "verbose": False
            },
            "personality": {
                "assertiveness": {
                    "base_level": 0.6,
                    "adaptation_rate": 0.1,
                    "min_level": 0.1,
                    "max_level": 0.9
                },
                "empathy": {
                    "base_level": 0.8,
                    "adaptation_rate": 0.1,
                    "min_level": 0.3,
                    "max_level": 1.0
                },
                "curiosity": {
                    "base_level": 0.9,
                    "adaptation_rate": 0.1,
                    "min_level": 0.2,
                    "max_level": 1.0
                }
            },
            "memory": {
                "short_term": {
                    "capacity": 50,
                    "decay_rate": 0.95,
                    "importance_threshold": 0.3
                },
                "long_term": {
                    "storage_threshold": 0.7,
                    "max_entries": 1000,
                    "consolidation_interval": 3600  # seconds
                }
            },
            "emotion": {
                "sensitivity": 0.6,
                "mood_persistence": 0.8,
                "default_mood": "neutral",
                "trigger_thresholds": {
                    "joy": 0.7,
                    "sadness": 0.6,
                    "anger": 0.8,
                    "fear": 0.7,
                    "surprise": 0.6
                }
            },
            "cognition": {
                "processing_depth": 3,
                "decision_threshold": 0.6,
                "context_window": 10,
                "analysis_timeout": 30  # seconds
            },
            "interface": {
                "cli_enabled": True,
                "api_enabled": True,
                "gradio_enabled": True,
                "api_port": 8000,
                "gradio_port": 7860,
                "input_timeout": 300,  # seconds
                "max_input_length": 2048
            },
            "skills": {
                "analog_hack": {
                    "enabled": True,
                    "trigger_words": ["hack", "creative", "workaround", "solution"]
                },
                "scheduling": {
                    "enabled": True,
                    "trigger_words": ["schedule", "plan", "calendar", "remind"]
                },
                "translation": {
                    "enabled": True,
                    "trigger_words": ["translate", "language", "convert"]
                }
            },
            "extensions": {
                "enabled": True,
                "auto_load": True,
                "extension_dir": "extensions/"
            },
            "logging": {
                "level": "INFO",
                "file": "lacia.log",
                "max_size": "10MB",
                "backup_count": 5
            }
        }
    
    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration values"""
        try:
            # Validate model config
            model_config = config.get("model", {})
            if not isinstance(model_config.get("n_ctx"), int) or model_config.get("n_ctx") < 256:
                config["model"]["n_ctx"] = 2048
            
            # Validate personality ranges
            for trait in ["assertiveness", "empathy", "curiosity"]:
                trait_config = config["personality"].get(trait, {})
                if not (0.0 <= trait_config.get("base_level", 0.5) <= 1.0):
                    config["personality"][trait]["base_level"] = 0.5
            
            # Validate memory config
            memory_config = config.get("memory", {})
            short_term = memory_config.get("short_term", {})
            if not isinstance(short_term.get("capacity"), int) or short_term.get("capacity") < 10:
                config["memory"]["short_term"]["capacity"] = 50
            
            return True
            
        except Exception as e:
            self.logger.error(f"Config validation error: {e}")
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self.config.copy()
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """Update configuration with new values"""
        try:
            def deep_update(base_dict, update_dict):
                for key, value in update_dict.items():
                    if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                        deep_update(base_dict[key], value)
                    else:
                        base_dict[key] = value
            
            deep_update(self.config, updates)
            self._validate_config(self.config)
            self.save_config()
            return True
            
        except Exception as e:
            self.logger.error(f"Config update error: {e}")
            return False
    
    def save_config(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Save configuration to file"""
        try:
            config_to_save = config if config is not None else self.config
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path) if os.path.dirname(self.config_path) else ".", exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Config save error: {e}")
            return False
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get specific configuration section"""
        return self.config.get(section, {})
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to defaults"""
        try:
            self.config = self._get_default_config()
            return self.save_config()
        except Exception as e:
            self.logger.error(f"Config reset error: {e}")
            return False

def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Convenience function to load configuration"""
    manager = ConfigManager(config_path)
    return manager.get_config()

def create_default_config(config_path: str = "config.json") -> bool:
    """Create default configuration file"""
    try:
        manager = ConfigManager(config_path)
        return manager.save_config()
    except Exception:
        return False
