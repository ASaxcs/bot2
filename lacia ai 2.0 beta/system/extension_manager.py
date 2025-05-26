"""
Extension Manager for Lacia AI
Handles loading and managing system extensions
"""

import os
import sys
import json
import logging
import importlib.util
from typing import Dict, List, Any, Optional
from pathlib import Path

class ExtensionManager:
    """Manages system extensions and plugins"""
    
    def __init__(self, extension_dir: str = "extensions/"):
        self.extension_dir = Path(extension_dir)
        self.loaded_extensions = {}
        self.extension_metadata = {}
        self.logger = logging.getLogger(__name__)
        
        # Create extension directory if it doesn't exist
        self.extension_dir.mkdir(parents=True, exist_ok=True)
    
    def load_extensions(self) -> Dict[str, Any]:
        """Load all available extensions"""
        if not self.extension_dir.exists():
            self.logger.info("Extension directory not found, creating...")
            self.extension_dir.mkdir(parents=True, exist_ok=True)
            return {}
        
        loaded_count = 0
        
        for extension_path in self.extension_dir.iterdir():
            if extension_path.is_dir() and not extension_path.name.startswith('.'):
                try:
                    if self._load_extension(extension_path):
                        loaded_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to load extension {extension_path.name}: {e}")
        
        self.logger.info(f"Loaded {loaded_count} extensions")
        return self.loaded_extensions
    
    def _load_extension(self, extension_path: Path) -> bool:
        """Load a single extension"""
        extension_name = extension_path.name
        
        # Check for manifest file
        manifest_path = extension_path / "manifest.json"
        if not manifest_path.exists():
            self.logger.warning(f"Extension {extension_name} missing manifest.json")
            return False
        
        try:
            # Load manifest
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            # Validate manifest
            if not self._validate_manifest(manifest):
                self.logger.error(f"Invalid manifest for extension {extension_name}")
                return False
            
            # Load main module
            main_module_path = extension_path / manifest.get("main", "main.py")
            if not main_module_path.exists():
                self.logger.error(f"Main module not found for extension {extension_name}")
                return False
            
            # Import the extension module
            spec = importlib.util.spec_from_file_location(
                f"extensions.{extension_name}",
                main_module_path
            )
            
            if spec is None or spec.loader is None:
                self.logger.error(f"Could not load spec for extension {extension_name}")
                return False
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[f"extensions.{extension_name}"] = module
            spec.loader.exec_module(module)
            
            # Initialize extension
            if hasattr(module, 'Extension'):
                extension_instance = module.Extension()
                
                # Validate extension interface
                if not self._validate_extension_interface(extension_instance):
                    self.logger.error(f"Extension {extension_name} has invalid interface")
                    return False
                
                # Store extension
                self.loaded_extensions[extension_name] = extension_instance
                self.extension_metadata[extension_name] = manifest
                
                self.logger.info(f"Loaded extension: {extension_name} v{manifest.get('version', '1.0.0')}")
                return True
            else:
                self.logger.error(f"Extension {extension_name} missing Extension class")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to load extension {extension_name}: {e}")
            return False
    
    def _validate_manifest(self, manifest: Dict[str, Any]) -> bool:
        """Validate extension manifest"""
        required_fields = ["name", "version", "description"]
        
        for field in required_fields:
            if field not in manifest:
                return False
        
        # Check version format
        version = manifest.get("version", "")
        if not isinstance(version, str) or not version:
            return False
        
        return True
    
    def _validate_extension_interface(self, extension) -> bool:
        """Validate extension has required interface methods"""
        required_methods = ["initialize", "process", "shutdown"]
        
        for method in required_methods:
            if not hasattr(extension, method) or not callable(getattr(extension, method)):
                return False
        
        return True
    
    def get_extension(self, name: str) -> Optional[Any]:
        """Get loaded extension by name"""
        return self.loaded_extensions.get(name)
    
    def list_extensions(self) -> List[Dict[str, Any]]:
        """List all loaded extensions with metadata"""
        result = []
        
        for name, extension in self.loaded_extensions.items():
            metadata = self.extension_metadata.get(name, {})
            result.append({
                "name": name,
                "version": metadata.get("version", "unknown"),
                "description": metadata.get("description", ""),
                "status": "loaded",
                "instance": extension
            })
        
        return result
    
    def unload_extension(self, name: str) -> bool:
        """Unload an extension"""
        try:
            if name in self.loaded_extensions:
                extension = self.loaded_extensions[name]
                
                # Call shutdown if available
                if hasattr(extension, 'shutdown'):
                    extension.shutdown()
                
                # Remove from loaded extensions
                del self.loaded_extensions[name]
                del self.extension_metadata[name]
                
                # Remove from sys.modules
                module_name = f"extensions.{name}"
                if module_name in sys.modules:
                    del sys.modules[module_name]
                
                self.logger.info(f"Unloaded extension: {name}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to unload extension {name}: {e}")
            return False
    
    def reload_extension(self, name: str) -> bool:
        """Reload an extension"""
        try:
            if name in self.loaded_extensions:
                # Get extension path
                extension_path = self.extension_dir / name
                
                if not extension_path.exists():
                    return False
                
                # Unload first
                self.unload_extension(name)
                
                # Reload
                return self._load_extension(extension_path)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to reload extension {name}: {e}")
            return False
    
    def create_extension_template(self, name: str, description: str = "") -> bool:
        """Create a template extension"""
        try:
            extension_path = self.extension_dir / name
            extension_path.mkdir(parents=True, exist_ok=True)
            
            # Create manifest
            manifest = {
                "name": name,
                "version": "1.0.0",
                "description": description or f"Extension: {name}",
                "author": "User",
                "main": "main.py"
            }
            
            manifest_path = extension_path / "manifest.json"
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)
            
            # Create main.py template
            main_template = f'''"""
{name.title()} Extension for Lacia AI
{description}
"""

import logging
from typing import Dict, Any, Optional

class Extension:
    """Main extension class"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.name = "{name}"
        self.initialized = False
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize the extension"""
        try:
            self.logger.info(f"Initializing {{self.name}} extension")
            
            # Your initialization code here
            
            self.initialized = True
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize {{self.name}}: {{e}}")
            return False
    
    def process(self, input_data: Any, context: Dict[str, Any]) -> Optional[Any]:
        """Process input data"""
        if not self.initialized:
            return None
        
        try:
            # Your processing logic here
            self.logger.info(f"Processing data in {{self.name}}")
            
            # Example: return modified input or response
            return None
            
        except Exception as e:
            self.logger.error(f"Processing error in {{self.name}}: {{e}}")
            return None
    
    def shutdown(self) -> bool:
        """Shutdown the extension"""
        try:
            self.logger.info(f"Shutting down {{self.name}} extension")
            
            # Your cleanup code here
            
            self.initialized = False
            return True
            
        except Exception as e:
            self.logger.error(f"Shutdown error in {{self.name}}: {{e}}")
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """Get extension information"""
        return {{
            "name": self.name,
            "initialized": self.initialized,
            "description": "{description or f'Extension: {name}'}"
        }}
'''
            
            main_path = extension_path / "main.py"
            with open(main_path, 'w', encoding='utf-8') as f:
                f.write(main_template)
            
            # Create README
            readme_content = f'''# {name.title()} Extension

{description}

## Installation

This extension is automatically loaded by Lacia AI.

## Configuration

Add configuration options to your Lacia AI config.json under:

```json
{{
  "extensions": {{
    "{name}": {{
      "enabled": true,
      // your extension config here
    }}
  }}
}}
```

## Usage

This extension processes inputs automatically when loaded.
'''
            
            readme_path = extension_path / "README.md"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            self.logger.info(f"Created extension template: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create extension template {name}: {e}")
            return False
    
    def get_extension_status(self) -> Dict[str, Any]:
        """Get overall extension system status"""
        return {
            "extension_dir": str(self.extension_dir),
            "loaded_count": len(self.loaded_extensions),
            "extensions": list(self.loaded_extensions.keys()),
            "available_extensions": self._scan_available_extensions()
        }
    
    def _scan_available_extensions(self) -> List[str]:
        """Scan for available extensions in directory"""
        available = []
        
        if not self.extension_dir.exists():
            return available
        
        for item in self.extension_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                manifest_path = item / "manifest.json"
                if manifest_path.exists():
                    available.append(item.name)
        
        return available
