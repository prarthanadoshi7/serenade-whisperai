"""
System requirements checker.
"""

import sys
import platform
import subprocess
from pathlib import Path
from typing import List, Tuple
from loguru import logger


class SystemCheck:
    """System requirements and environment checker."""
    
    def __init__(self, config):
        """Initialize system checker.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def check_python_version(self) -> bool:
        """Check Python version."""
        logger.info("Checking Python version...")
        
        major, minor = sys.version_info[:2]
        
        if major < 3 or (major == 3 and minor < 9):
            self.errors.append(f"Python 3.9+ required, found {major}.{minor}")
            return False
        
        logger.success(f"Python {major}.{minor} detected")
        return True
    
    def check_dependencies(self) -> bool:
        """Check if required packages are installed."""
        logger.info("Checking dependencies...")
        
        required_packages = [
            "whisper",
            "torch",
            "PyQt6",
            "pyaudio",
            "pyautogui",
            "tree_sitter",
            "fastapi",
            "uvicorn"
        ]
        
        missing = []
        
        for package in required_packages:
            try:
                __import__(package)
                logger.debug(f"✓ {package}")
            except ImportError:
                missing.append(package)
                logger.warning(f"✗ {package}")
        
        if missing:
            self.errors.append(
                f"Missing packages: {', '.join(missing)}. "
                "Run: pip install -r requirements.txt"
            )
            return False
        
        logger.success("All dependencies installed")
        return True
    
    def check_cuda_availability(self) -> bool:
        """Check CUDA availability for GPU acceleration."""
        logger.info("Checking CUDA availability...")
        
        try:
            import torch
            
            if torch.cuda.is_available():
                device_name = torch.cuda.get_device_name(0)
                logger.success(f"CUDA available: {device_name}")
                return True
            else:
                self.warnings.append(
                    "CUDA not available. Using CPU (slower performance)"
                )
                logger.warning("CUDA not available, will use CPU")
                return True  # Not critical
                
        except Exception as e:
            self.warnings.append(f"Could not check CUDA: {e}")
            return True
    
    def check_audio_devices(self) -> bool:
        """Check audio input devices."""
        logger.info("Checking audio devices...")
        
        try:
            import pyaudio
            
            p = pyaudio.PyAudio()
            device_count = p.get_device_count()
            
            # Find input devices
            input_devices = []
            for i in range(device_count):
                device_info = p.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    input_devices.append(device_info['name'])
            
            p.terminate()
            
            if not input_devices:
                self.errors.append("No audio input devices found")
                return False
            
            logger.success(f"Found {len(input_devices)} input device(s)")
            for device in input_devices:
                logger.debug(f"  - {device}")
            
            return True
            
        except Exception as e:
            self.errors.append(f"Audio device check failed: {e}")
            return False
    
    def check_disk_space(self) -> bool:
        """Check available disk space for models."""
        logger.info("Checking disk space...")
        
        try:
            import shutil
            
            # Check space in home directory
            home = Path.home()
            stat = shutil.disk_usage(home)
            
            # Model sizes (approximate)
            model_sizes = {
                "tiny": 0.04,  # GB
                "base": 0.14,
                "small": 0.46,
                "medium": 1.42,
                "large": 2.87,
                "large-v3": 2.87
            }
            
            required_model = self.config.get("whisper.model", "base")
            required_space = model_sizes.get(required_model, 1.0)
            
            # Need at least 2x model size + 1GB buffer
            required_gb = (required_space * 2) + 1
            available_gb = stat.free / (1024**3)
            
            if available_gb < required_gb:
                self.errors.append(
                    f"Insufficient disk space. Need {required_gb:.1f}GB, "
                    f"have {available_gb:.1f}GB"
                )
                return False
            
            logger.success(f"Disk space OK: {available_gb:.1f}GB available")
            return True
            
        except Exception as e:
            self.warnings.append(f"Could not check disk space: {e}")
            return True
    
    def check_permissions(self) -> bool:
        """Check system permissions."""
        logger.info("Checking permissions...")
        
        # Check write permissions for logs and cache
        required_dirs = [
            Path("logs"),
            Path("cache"),
            Path("models")
        ]
        
        for dir_path in required_dirs:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                
                # Try to write a test file
                test_file = dir_path / ".test"
                test_file.write_text("test")
                test_file.unlink()
                
                logger.debug(f"✓ Write access to {dir_path}")
                
            except Exception as e:
                self.errors.append(f"No write access to {dir_path}: {e}")
                return False
        
        logger.success("Permissions OK")
        return True
    
    def check_platform_support(self) -> bool:
        """Check if platform is supported."""
        logger.info("Checking platform...")
        
        system = platform.system()
        supported = ["Windows", "Darwin", "Linux"]
        
        if system not in supported:
            self.errors.append(f"Unsupported platform: {system}")
            return False
        
        logger.success(f"Platform: {system} {platform.release()}")
        return True
    
    def run_all_checks(self) -> bool:
        """Run all system checks.
        
        Returns:
            True if all checks pass
        """
        checks = [
            self.check_python_version,
            self.check_platform_support,
            self.check_dependencies,
            self.check_cuda_availability,
            self.check_audio_devices,
            self.check_disk_space,
            self.check_permissions
        ]
        
        results = []
        
        for check in checks:
            try:
                results.append(check())
            except Exception as e:
                logger.error(f"Check failed: {check.__name__}: {e}")
                results.append(False)
        
        # Display summary
        logger.info("\n" + "="*60)
        logger.info("System Check Summary")
        logger.info("="*60)
        
        if self.errors:
            logger.error("Errors:")
            for error in self.errors:
                logger.error(f"  • {error}")
        
        if self.warnings:
            logger.warning("Warnings:")
            for warning in self.warnings:
                logger.warning(f"  • {warning}")
        
        if not self.errors and not self.warnings:
            logger.success("All checks passed!")
        
        logger.info("="*60 + "\n")
        
        return all(results) and len(self.errors) == 0
