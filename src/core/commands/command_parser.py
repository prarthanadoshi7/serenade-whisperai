"""
Command parsing logic.
"""

import re
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from loguru import logger


@dataclass
class ParsedCommand:
    """Parsed command data."""
    action: str
    target: Optional[str] = None
    value: Optional[str] = None
    line_number: Optional[int] = None
    parameters: Optional[Dict[str, Any]] = field(default_factory=dict)


class CommandParser:
    """Parse voice commands into structured format."""
    
    # Command patterns
    PATTERNS = {
        # Navigation
        r'go to line (\d+)': ('goto_line', 'line_number'),
        r'go to function (.+)': ('goto_function', 'target'),
        r'go to class (.+)': ('goto_class', 'target'),
        r'go to method (.+)': ('goto_method', 'target'),
        r'next function': ('next_function', None),
        r'previous function': ('prev_function', None),
        r'next line': ('next_line', None),
        r'previous line': ('prev_line', None),
        r'scroll (up|down)': ('scroll', 'target'),
        r'page (up|down)': ('page', 'target'),
        
        # Editing
        r'add function (.+)': ('add_function', 'target'),
        r'add class (.+)': ('add_class', 'target'),
        r'add method (.+)': ('add_method', 'target'),
        r'create function (.+)': ('add_function', 'target'),
        r'create class (.+)': ('add_class', 'target'),
        r'delete line': ('delete_line', None),
        r'delete function (.+)': ('delete_function', 'target'),
        r'delete class (.+)': ('delete_class', 'target'),
        r'remove line': ('delete_line', None),
        r'insert (.+)': ('insert', 'value'),
        r'type (.+)': ('type', 'value'),
        r'add comment (.+)': ('add_comment', 'value'),
        
        # Selection
        r'select line (\d+)': ('select_line', 'line_number'),
        r'select function (.+)': ('select_function', 'target'),
        r'select class (.+)': ('select_class', 'target'),
        r'select all': ('select_all', None),
        r'select word': ('select_word', None),
        r'select line': ('select_current_line', None),
        
        # Change/Replace
        r'change (.+) to (.+)': ('change', 'target_value'),
        r'rename (.+) to (.+)': ('rename', 'target_value'),
        r'replace (.+) with (.+)': ('replace', 'target_value'),
        
        # Clipboard
        r'copy': ('copy', None),
        r'cut': ('cut', None),
        r'paste': ('paste', None),
        r'duplicate line': ('duplicate_line', None),
        r'copy line': ('copy_line', None),
        
        # Undo/Redo
        r'undo': ('undo', None),
        r'redo': ('redo', None),
        
        # Save/Open
        r'save file': ('save', None),
        r'save': ('save', None),
        r'save as (.+)': ('save_as', 'value'),
        r'open file (.+)': ('open_file', 'value'),
        r'close file': ('close_file', None),
        r'new file': ('new_file', None),
        
        # Search/Find
        r'find (.+)': ('find', 'value'),
        r'search (.+)': ('search', 'value'),
        r'find next': ('find_next', None),
        r'find previous': ('find_previous', None),
        
        # Format
        r'format document': ('format_document', None),
        r'format selection': ('format_selection', None),
        r'indent': ('indent', None),
        r'unindent': ('unindent', None),
        r'comment out': ('comment_out', None),
        r'uncomment': ('uncomment', None),
    }
    
    def __init__(self, config):
        """Initialize parser."""
        self.config = config
        
        # Compile patterns
        self.compiled_patterns = []
        for pattern, (action, param_type) in self.PATTERNS.items():
            self.compiled_patterns.append((
                re.compile(pattern, re.IGNORECASE),
                action,
                param_type
            ))
        
        logger.info(f"CommandParser initialized with {len(self.compiled_patterns)} patterns")
    
    def parse(self, text: str) -> Optional[ParsedCommand]:
        """Parse text into command.
        
        Args:
            text: Input text
            
        Returns:
            Parsed command or None
        """
        text = text.strip().lower()
        
        for pattern, action, param_type in self.compiled_patterns:
            match = pattern.match(text)
            
            if match:
                command = ParsedCommand(action=action)
                
                if param_type == 'target' and match.groups():
                    command.target = match.group(1)
                
                elif param_type == 'value' and match.groups():
                    command.value = match.group(1)
                
                elif param_type == 'line_number' and match.groups():
                    try:
                        command.line_number = int(match.group(1))
                    except ValueError:
                        logger.warning(f"Invalid line number: {match.group(1)}")
                        return None
                
                elif param_type == 'target_value' and len(match.groups()) >= 2:
                    command.target = match.group(1)
                    command.value = match.group(2)
                
                logger.debug(f"Parsed: {text} -> action={command.action}")
                return command
        
        logger.warning(f"No pattern matched: {text}")
        return None
