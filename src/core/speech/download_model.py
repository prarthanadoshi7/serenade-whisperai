#!/usr/bin/env python3
"""Download Whisper models."""

import whisper
from pathlib import Path
from loguru import logger
import sys

def download_model(model_name: str = "base"):
    """Download Whisper model.
    
    Args:
        model_name: Model size (tiny, base, small, medium, large, large-v3)
    """
    logger.info(f"Downloading Whisper model: {model_name}")
    
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    try:
        model = whisper.load_model(model_name, download_root=str(models_dir))
        logger.success(f"Model {model_name} downloaded successfully")
        logger.info(f"Model saved to: {models_dir}")
        return model
    except Exception as e:
        logger.error(f"Failed to download model: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Download Whisper models")
    parser.add_argument(
        "model",
        nargs="?",
        default="base",
        choices=["tiny", "base", "small", "medium", "large", "large-v3"],
        help="Model size to download"
    )
    
    args = parser.parse_args()
    download_model(args.model)
