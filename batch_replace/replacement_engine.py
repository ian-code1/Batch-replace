"""
Replacement engine that handles string and regex search and replace operations.
"""

import re
from typing import Tuple
import logging


class ReplacementEngine:
    """
    Handles search and replace operations with support for both exact string
    and regular expression matching.
    """
    
    def __init__(self, pattern: str, replace: str, use_regex: bool = False):
        """
        Initialize the replacement engine.
        
        Args:
            pattern: Search pattern (string or regex)
            replace: Replacement string
            use_regex: If True, treat pattern as regular expression
        """
        self.pattern = pattern
        self.replace = replace
        self.use_regex = use_regex
        self.logger = logging.getLogger(__name__)
        
        # Compile regex if needed
        self._regex = None
        if use_regex:
            try:
                self._regex = re.compile(pattern, re.MULTILINE | re.DOTALL)
            except re.error as e:
                self.logger.error(f"Invalid regex pattern '{pattern}': {e}")
                raise ValueError(f"Invalid regex pattern: {e}")
    
    def apply(self, content: str) -> Tuple[str, int]:
        """
        Apply search and replace to the content.
        
        Args:
            content: Input text
            
        Returns:
            Tuple of (modified_content, replacement_count)
        """
        if not content:
            return content, 0
        
        if self.use_regex:
            return self._apply_regex(content)
        else:
            return self._apply_string(content)
    
    def _apply_string(self, content: str) -> Tuple[str, int]:
        """
        Apply exact string replacement.
        
        Args:
            content: Input text
            
        Returns:
            Tuple of (modified_content, replacement_count)
        """
        count = content.count(self.pattern)
        if count == 0:
            return content, 0
        
        # Use replace method for exact matches
        modified = content.replace(self.pattern, self.replace)
        return modified, count
    
    def _apply_regex(self, content: str) -> Tuple[str, int]:
        """
        Apply regular expression replacement.
        
        Args:s
            content: Input text
            
        Returns:
            Tuple of (modified_content, replacement_count)
        """
        if not self._regex:
            return content, 0
        
        try:
            # Count matches first
            matches = list(self._regex.finditer(content))
            count = len(matches)
            
            if count == 0:
                return content, 0
            
            # Perform replacement
            modified = self._regex.sub(self.replace, content)
            return modified, count
            
        except Exception as e:
            self.logger.error(f"Error applying regex replacement: {e}")
            return content, 0