"""
Configuration Manager for Lacia AI
Handles loading, saving, and managing system configuration
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path

class ConfigManager:
    """Manages system configuration with validation and defaults"""
    
    def __init__(self, config_path: Union[str, Path] = "config.json"):
        # Ensure config_path is always a string
        self.config_path = str(config_path) if isinstance(config_path, Path) else config_path
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration with fallback to defaults"""
        default_config = self._get_default_config()
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults using deep merge
                    merged_config = self._deep_merge(default_config, loaded_config)
                    self._validate_config(merged_config)
                    print(f"✅ Configuration loaded from: {self.config_path}")
                    return merged_config
            else:
                # Create default config file
                print(f"📝 Creating default configuration at: {self.config_path}")
                self._save_config_internal(default_config)
                return default_config
                
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in config file: {e}")
            print("🔄 Using default configuration...")
            return default_config
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            print("🔄 Using default configuration...")
            return default_config
    
    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = base.copy()
        
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "model": {
                "model_id": "TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
                "model_basename": "mistral-7b-instruct-v0.2.Q4_K_M.gguf",
                "model_path": os.path.join("models", "mistral-7b-instruct-v0.2.Q4_K_M.gguf"),
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
                    "consolidation_interval": 3600
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
                "analysis_timeout": 30
            },
            "interface": {
                "cli_enabled": True,
                "api_enabled": True,
                "gradio_enabled": True,
                "api_port": 8000,
                "gradio_port": 7860,
                "input_timeout": 300,
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
                "extension_dir": "extensions"
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
            if "model" in config:
                model_config = config["model"]
                
                # Ensure n_ctx is valid
                if not isinstance(model_config.get("n_ctx"), int) or model_config.get("n_ctx") < 256:
                    model_config["n_ctx"] = 2048
                
                # Ensure temperature is in valid range
                temp = model_config.get("temperature", 0.7)
                if not isinstance(temp, (int, float)) or temp < 0 or temp > 2:
                    model_config["temperature"] = 0.7
                
                # Ensure model_path is a string
                if "model_path" not in model_config or not isinstance(model_config["model_path"], str):
                    model_config["model_path"] = os.path.join("models", "mistral-7b-instruct-v0.2.Q4_K_M.gguf")
            
            # Validate personality ranges
            if "personality" in config:
                for trait in ["assertiveness", "empathy", "curiosity"]:
                    if trait in config["personality"]:
                        trait_config = config["personality"][trait]
                        base_level = trait_config.get("base_level", 0.5)
                        
                        if not isinstance(base_level, (int, float)) or not (0.0 <= base_level <= 1.0):
                            trait_config["base_level"] = 0.5
                        
                        # Validate min/max levels
                        min_level = trait_config.get("min_level", 0.0)
                        max_level = trait_config.get("max_level", 1.0)
                        
                        if not isinstance(min_level, (int, float)) or not (0.0 <= min_level <= 1.0):
                            trait_config["min_level"] = 0.0
                        if not isinstance(max_level, (int, float)) or not (0.0 <= max_level <= 1.0):
                            trait_config["max_level"] = 1.0
            
            # Validate memory config
            if "memory" in config:
                if "short_term" in config["memory"]:
                    st_config = config["memory"]["short_term"]
                    capacity = st_config.get("capacity", 50)
                    if not isinstance(capacity, int) or capacity < 10:
                        st_config["capacity"] = 50
                
                if "long_term" in config["memory"]:
                    lt_config = config["memory"]["long_term"]
                    max_entries = lt_config.get("max_entries", 1000)
                    if not isinstance(max_entries, int) or max_entries < 100:
                        lt_config["max_entries"] = 1000
            
            # Validate interface ports
            if "interface" in config:
                interface_config = config["interface"]
                for port_key in ["api_port", "gradio_port"]:
                    port = interface_config.get(port_key)
                    if not isinstance(port, int) or port < 1024 or port > 65535:
                        interface_config[port_key] = 8000 if port_key == "api_port" else 7860
            
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
            self.config = self._deep_merge(self.config, updates)
            self._validate_config(self.config)
            return self.save_config()
            
        except Exception as e:
            self.logger.error(f"Config update error: {e}")
            return False
    
    def _save_config_internal(self, config: Dict[str, Any]) -> bool:
        """Internal method to save configuration"""
        try:
            # Ensure directory exists
            config_dir = os.path.dirname(self.config_path)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
            
            # Write configuration file
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Config save error: {e}")
            return False
    
    def save_config(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Save configuration to file"""
        config_to_save = config if config is not None else self.config
        return self._save_config_internal(config_to_save)
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get specific configuration section"""
        return self.config.get(section, {})
    
    def set_section(self, section: str, data: Dict[str, Any]) -> bool:
        """Set specific configuration section"""
        try:
            self.config[section] = data
            self._validate_config(self.config)
            return self.save_config()
        except Exception as e:
            self.logger.error(f"Set section error: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to defaults"""
        try:
            self.config = self._get_default_config()
            return self.save_config()
        except Exception as e:
            self.logger.error(f"Config reset error: {e}")
            return False
    
    def get_model_path(self) -> str:
        """Get the model file path"""
        return self.config.get("model", {}).get("model_path", "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf")
    
    def set_model_path(self, path: str) -> bool:
        """Set the model file path"""
        try:
            if "model" not in self.config:
                self.config["model"] = {}
            self.config["model"]["model_path"] = str(path)
            return self.save_config()
        except Exception as e:
            self.logger.error(f"Set model path error: {e}")
            return False
    
    def is_valid(self) -> bool:
        """Check if current configuration is valid"""
        return self._validate_config(self.config.copy())


def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Convenience function to load configuration"""
    try:
        manager = ConfigManager(config_path)
        return manager.get_config()
    except Exception as e:
        print(f"❌ Error in load_config: {e}")
        # Return minimal default config
        return {
            "model": {
                "model_path": os.path.join("models", "mistral-7b-instruct-v0.2.Q4_K_M.gguf"),
                "n_ctx": 2048,
                "max_tokens": 512,
                "temperature": 0.7
            }
        }


def create_default_config(config_path: str = "config.json") -> bool:
    """Create default configuration file"""
    try:
        manager = ConfigManager()
        manager.config_path = config_path
        return manager.save_config()
    except Exception as e:
        print(f"❌ Error creating default config: {e}")
        return False


# Backward compatibility
def get_config_manager(config_path: str = "config.json") -> ConfigManager:
    """Get a ConfigManager instance"""
    return ConfigManager(config_path)