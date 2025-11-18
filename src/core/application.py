"""
Main application class for Serenade WhisperAI.
"""

import asyncio
import sys
from typing import Optional
from loguru import logger

from .config import Config
from .audio.audio_manager import AudioManager
from .speech.whisper_engine import WhisperEngine
from .commands.command_processor import CommandProcessor
from .automation.automation_manager import AutomationManager


class Application:
    """Main application orchestrator."""
    
    def __init__(self, config: Config, headless: bool = False, server_only: bool = False):
        """Initialize application.
        
        Args:
            config: Configuration object
            headless: Run without GUI
            server_only: Run only the API server
        """
        self.config = config
        self.headless = headless
        self.server_only = server_only
        
        # Core components
        self.audio_manager: Optional[AudioManager] = None
        self.whisper_engine: Optional[WhisperEngine] = None
        self.command_processor: Optional[CommandProcessor] = None
        self.automation_manager: Optional[AutomationManager] = None
        self.gui = None
        self.server = None
        
        # State
        self.running = False
        self.loop: Optional[asyncio.AbstractEventLoop] = None
    
    def initialize_components(self):
        """Initialize all application components."""
        logger.info("Initializing core components...")
        
        try:
            # Initialize Whisper engine
            logger.info("Loading Whisper model...")
            self.whisper_engine = WhisperEngine(self.config)
            logger.success("Whisper engine initialized")
            
            # Initialize audio manager
            logger.info("Setting up audio capture...")
            self.audio_manager = AudioManager(self.config)
            logger.success("Audio manager initialized")
            
            # Initialize automation manager
            logger.info("Setting up system automation...")
            self.automation_manager = AutomationManager(self.config)
            logger.success("Automation manager initialized")
            
            # Initialize command processor
            logger.info("Loading command processor...")
            self.command_processor = CommandProcessor(
                config=self.config,
                automation_manager=self.automation_manager
            )
            logger.success("Command processor initialized")
            
            # Initialize GUI if not headless
            if not self.headless and not self.server_only:
                logger.info("Initializing GUI...")
                from gui.main_window import MainWindow
                from PyQt6.QtWidgets import QApplication
                
                self.qt_app = QApplication(sys.argv)
                self.gui = MainWindow(
                    config=self.config,
                    audio_manager=self.audio_manager,
                    whisper_engine=self.whisper_engine,
                    command_processor=self.command_processor
                )
                logger.success("GUI initialized")
            
            # Initialize API server
            if self.server_only or self.config.get("server.enabled", False):
                logger.info("Initializing API server...")
                from server.api_server import APIServer
                
                self.server = APIServer(
                    config=self.config,
                    audio_manager=self.audio_manager,
                    whisper_engine=self.whisper_engine,
                    command_processor=self.command_processor
                )
                logger.success("API server initialized")
            
            logger.success("All components initialized successfully")
            
        except Exception as e:
            logger.exception(f"Failed to initialize components: {e}")
            raise
    
    def setup_callbacks(self):
        """Setup callbacks between components."""
        logger.info("Setting up component callbacks...")
        
        # Connect audio manager to whisper engine
        self.audio_manager.on_audio_ready = self._handle_audio_ready
        
        # Connect whisper engine to command processor
        self.whisper_engine.on_transcription_ready = self._handle_transcription
        
        # Connect command processor callbacks
        self.command_processor.on_command_executed = self._handle_command_executed
        self.command_processor.on_command_error = self._handle_command_error
        
        logger.success("Callbacks configured")
    
    async def _handle_audio_ready(self, audio_data: bytes):
        """Handle audio data from audio manager."""
        logger.debug("Audio data received, starting transcription...")
        
        try:
            transcription = await self.whisper_engine.transcribe_async(audio_data)
            logger.info(f"Transcription: {transcription}")
            
            if self.gui:
                self.gui.update_transcription(transcription)
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
    
    async def _handle_transcription(self, transcription: str, confidence: float):
        """Handle transcription from Whisper engine."""
        logger.info(f"Processing transcription: '{transcription}' (confidence: {confidence:.2f})")
        
        try:
            # Process command
            result = await self.command_processor.process_command(transcription)
            
            if result.success:
                logger.success(f"Command executed: {result.command}")
            else:
                logger.warning(f"Command failed: {result.error}")
            
        except Exception as e:
            logger.error(f"Command processing failed: {e}")
    
    async def _handle_command_executed(self, command: str, result: dict):
        """Handle successful command execution."""
        logger.debug(f"Command '{command}' executed successfully")
        
        if self.gui:
            self.gui.show_success_notification(command)
    
    async def _handle_command_error(self, command: str, error: str):
        """Handle command execution error."""
        logger.warning(f"Command '{command}' failed: {error}")
        
        if self.gui:
            self.gui.show_error_notification(error)
    
    def run(self) -> int:
        """Run the application.
        
        Returns:
            Exit code
        """
        try:
            # Initialize components
            self.initialize_components()
            
            # Setup callbacks
            self.setup_callbacks()
            
            self.running = True
            logger.info("Application started successfully")
            
            # Run based on mode
            if self.server_only:
                return self._run_server_mode()
            elif self.headless:
                return self._run_headless_mode()
            else:
                return self._run_gui_mode()
            
        except KeyboardInterrupt:
            logger.info("Shutdown requested")
            return 0
        except Exception as e:
            logger.exception(f"Application error: {e}")
            return 1
        finally:
            self.cleanup()
    
    def _run_gui_mode(self) -> int:
        """Run application with GUI."""
        logger.info("Running in GUI mode")
        
        try:
            self.gui.show()
            return self.qt_app.exec()
        except Exception as e:
            logger.exception(f"GUI error: {e}")
            return 1
    
    def _run_headless_mode(self) -> int:
        """Run application in headless mode."""
        logger.info("Running in headless mode")
        
        try:
            # Create event loop
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            # Start audio capture
            self.audio_manager.start()
            
            # Keep running
            self.loop.run_forever()
            
            return 0
            
        except KeyboardInterrupt:
            logger.info("Shutdown requested")
            return 0
        except Exception as e:
            logger.exception(f"Headless mode error: {e}")
            return 1
        finally:
            if self.loop:
                self.loop.close()
    
    def _run_server_mode(self) -> int:
        """Run application in server-only mode."""
        logger.info("Running in server-only mode")
        
        try:
            import uvicorn
            
            host = self.config.get("server.host", "127.0.0.1")
            port = self.config.get("server.port", 8765)
            
            uvicorn.run(
                self.server.app,
                host=host,
                port=port,
                log_level="info"
            )
            
            return 0
            
        except Exception as e:
            logger.exception(f"Server error: {e}")
            return 1
    
    def cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up resources...")
        
        self.running = False
        
        try:
            if self.audio_manager:
                self.audio_manager.stop()
            
            if self.whisper_engine:
                self.whisper_engine.cleanup()
            
            if self.automation_manager:
                self.automation_manager.cleanup()
            
            logger.info("Cleanup complete")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
