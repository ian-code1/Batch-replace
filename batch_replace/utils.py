"""
Utility functions for the batch replacement tool.
"""

import os
from pathlib import Path
from typing import Tuple
import logging


def validate_paths(source: str, destination: str, dry_run: bool = False) -> bool:
    """
    Validate source and destination paths.
    
    Args:
        source: Source directory path
        destination: Destination directory path
        dry_run: If True, skip destination write validation
        
    Returns:
        True if paths are valid, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    # Validate source directory
    source_path = Path(source)
    
    if not source_path.exists():
        logger.error(f"Source path does not exist: {source}")
        return False
    
    if not source_path.is_dir():
        logger.error(f"Source path is not a directory: {source}")
        return False
    
    # Validate destination (if not dry run)
    if not dry_run:
        dest_path = Path(destination)
        
        # Check if destination is inside source (prevent infinite recursion)
        try:
            if dest_path.resolve() == source_path.resolve():
                logger.error("Destination cannot be the same as source")
                return False
            
            # Check if destination is a subdirectory of source
            if dest_path.resolve().is_relative_to(source_path.resolve()):
                logger.error("Destination cannot be inside source directory")
                return False
        except Exception:
            # Fallback for older Python versions without is_relative_to
            try:
                source_resolved = source_path.resolve()
                dest_resolved = dest_path.resolve()
                if str(dest_resolved).startswith(str(source_resolved)):
                    logger.error("Destination cannot be inside source directory")
                    return False
            except Exception:
                pass
    
    return True


def get_file_size(file_path: Path) -> str:
    """
    Get human-readable file size.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Human-readable file size string
    """
    try:
        size = file_path.stat().st_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    except Exception:
        return "Unknown"