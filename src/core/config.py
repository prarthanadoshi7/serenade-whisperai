"""
Configuration management for Serenade WhisperAI.
"""

import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from loguru import logger


class Config:
    """Configuration manager."""
    
    DEFAULT_CONFIG = {
        "audio": {
            "sample_rate": 16000,
            "chunk_size": 1024,
            "channels": 1,
            "vad_mode": 3,
            "silence_duration": 1.5,
            "energy_threshold": 300,
            "buffer_size": 10
        },
        "whisper": {
            "model": "base",
            "device": "cpu",
            "language": "en",
            "fp16": False,
            "beam_size": 5,
            "best_of": 5,
            "temperature": 0.0,
            "compute_type": "default"
        },
        "commands": {
            "confidence_threshold": 0.7,
            "custom_commands_enabled": True,
            "custom_commands_path": "config/custom_commands.yml",
            "command_timeout": 30,
            "retry_on_failure": True
        },
        "automation": {
            "typing_delay": 0.01,
            "mouse_speed": 1.0,
            "failsafe": True,
            "pause_between_actions": 0.1
        },
        "gui": {
            "theme": "dark",
            "always_on_top": False,
            "show_transcriptions": True,
            "window_size": [800, 600],
            "opacity": 0.95
        },
        "server": {
            "host": "127.0.0.1",
            "port": 8765,
            "enable_cors": True,
            "max_connections": 10
        },
        "logging": {
            "level": "INFO",
            "file": "logs/serenade.log",
            "max_size": "10 MB",
            "backup_count": 5
        },
        "hotkeys": {
            "toggle_recording": "ctrl+shift+space",
            "cancel_command": "escape",
            "show_hide_gui": "ctrl+shift+h"
        },
        "performance": {
            "use_gpu": True,
            "max_threads": 4,
            "cache_enabled": True,
            "cache_size_mb": 512
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self._config = self.DEFAULT_CONFIG.copy()
        self._config_path = Path(config_path) if config_path else None
        
        if self._config_path and self._config_path.exists():
            self._load_from_file()
        else:
            logger.warning(f"Config file not found: {config_path}, using defaults")
    
    def _load_from_file(self):
        """Load configuration from YAML file."""
        try:
            with open(self._config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                if user_config:
                    self._deep_update(self._config, user_config)
                    logger.info(f"Loaded configuration from {self._config_path}")
        except Exception as e:
            logger.error(f"Failed to load config file: {e}")
    
    def _deep_update(self, base_dict: Dict, update_dict: Dict) -> Dict:
        """Recursively update nested dictionary."""
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict:
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
        return base_dict
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation.
        
        Args:
            key: Dot-separated key path (e.g., 'audio.sample_rate')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Set configuration value using dot notation.
        
        Args:
            key: Dot-separated key path
            value: Value to set
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            config = config.setdefault(k, {})
        
        config[keys[-1]] = value
    
    def save(self, path: Optional[str] = None):
        """Save configuration to file.
        
        Args:
            path: Path to save to (uses original path if not specified)
        """
        save_path = Path(path) if path else self._config_path
        
        if not save_path:
            logger.error("No path specified for saving configuration")
            return
        
        try:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, 'w') as f:
                yaml.dump(self._config, f, default_flow_style=False)
            
            logger.info(f"Configuration saved to {save_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def to_dict(self) -> Dict:
        """Get full configuration as dictionary."""
        return self._config.copy()
    
    def __repr__(self) -> str:
        return f"Config(path={self._config_path})"
