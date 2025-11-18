#!/usr/bin/env python3
"""
Serenade WhisperAI - Main Entry Point

A voice-controlled coding assistant powered by OpenAI Whisper.
"""

import sys
import argparse
from pathlib import Path
from loguru import logger

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from core.config import Config
from core.application import Application
from utils.system_check import SystemCheck


def setup_logging(config: Config):
    """Configure logging with loguru."""
    log_level = config.get("logging.level", "INFO")
    log_file = config.get("logging.file", "logs/serenade.log")
    
    # Remove default handler
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True
    )
    
    # Add file handler
    logger.add(
        log_file,
        rotation="10 MB",
        retention="1 week",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=log_level
    )


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Serenade WhisperAI - Voice-Controlled Coding Assistant"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yml",
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        choices=["tiny", "base", "small", "medium", "large", "large-v3"],
        help="Whisper model size (overrides config)"
    )
    
    parser.add_argument(
        "--device",
        type=str,
        choices=["cuda", "cpu"],
        help="Device to run model on (overrides config)"
    )
    
    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Run without GUI (headless mode)"
    )
    
    parser.add_argument(
        "--server-only",
        action="store_true",
        help="Run only the API server"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    # Parse arguments
    args = parse_arguments()
    
    # Load configuration
    config = Config(args.config)
    
    # Override config with CLI arguments
    if args.model:
        config.set("whisper.model", args.model)
    if args.device:
        config.set("whisper.device", args.device)
    if args.debug:
        config.set("logging.level", "DEBUG")
    
    # Setup logging
    setup_logging(config)
    
    logger.info("="*60)
    logger.info("Serenade WhisperAI Starting...")
    logger.info("="*60)
    
    try:
        # Run system checks
        logger.info("Running system checks...")
        system_check = SystemCheck(config)
        
        if not system_check.run_all_checks():
            logger.error("System checks failed. Please fix the issues and try again.")
            return 1
        
        logger.success("System checks passed!")
        
        # Create and run application
        logger.info("Initializing application...")
        app = Application(
            config=config,
            headless=args.no_gui,
            server_only=args.server_only
        )
        
        logger.info("Starting application...")
        return app.run()
        
    except KeyboardInterrupt:
        logger.info("\nShutdown requested by user")
        return 0
        
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
