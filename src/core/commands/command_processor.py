"""
Command processing and execution.
"""

import re
from typing import Optional, Callable
from dataclasses import dataclass
from loguru import logger

from .command_parser import CommandParser
from .command_executor import CommandExecutor


@dataclass
class CommandResult:
    """Command execution result."""
    success: bool
    command: str
    action: Optional[str] = None
    error: Optional[str] = None
    data: Optional[dict] = None


class CommandProcessor:
    """Process and execute voice commands."""
    
    def __init__(self, config, automation_manager):
        """Initialize command processor.
        
        Args:
            config: Application configuration
            automation_manager: Automation manager instance
        """
        self.config = config
        self.automation_manager = automation_manager
        
        # Components
        self.parser = CommandParser(config)
        self.executor = CommandExecutor(config, automation_manager)
        
        # Callbacks
        self.on_command_executed: Optional[Callable] = None
        self.on_command_error: Optional[Callable] = None
        
        # State
        self.last_command: Optional[str] = None
        
        logger.info("CommandProcessor initialized")
    
    async def process_command(self, transcription: str) -> CommandResult:
        """Process voice command.
        
        Args:
            transcription: Transcribed text
            
        Returns:
            Command result
        """
        try:
            # Clean transcription
            transcription = transcription.strip().lower()
            
            if not transcription:
                return CommandResult(
                    success=False,
                    command="",
                    error="Empty transcription"
                )
            
            logger.info(f"Processing command: '{transcription}'")
            
            # Parse command
            parsed = self.parser.parse(transcription)
            
            if not parsed:
                logger.warning(f"Could not parse command: {transcription}")
                return CommandResult(
                    success=False,
                    command=transcription,
                    error="Command not recognized"
                )
            
            # Execute command
            result = await self.executor.execute(parsed)
            
            # Store last command
            self.last_command = transcription
            
            # Trigger callbacks
            if result.success and self.on_command_executed:
                await self.on_command_executed(transcription, result.data or {})
            elif not result.success and self.on_command_error:
                await self.on_command_error(transcription, result.error or "Unknown error")
            
            return result
            
        except Exception as e:
            logger.exception(f"Command processing error: {e}")
            return CommandResult(
                success=False,
                command=transcription,
                error=str(e)
            )
