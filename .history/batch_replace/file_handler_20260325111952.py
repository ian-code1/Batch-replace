"""
File handling utilities for reading, writing, and traversing the filesystem.
Handles file type detection, encoding, and directory structure mirroring.
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Set
import logging
import chardet


class FileHandler:
    """
    Handles file system operations including file discovery, reading, writing,
    and maintaining directory structure.
    """
    
    # Common text file extensions
    TEXT_EXTENSIONS = {
        '.txt', '.md', '.rst', '.html', '.htm', '.css', '.js', '.jsx', '.ts', '.tsx',
        '.json', '.xml', '.yaml', '.yml', '.csv', '.log', '.ini', '.cfg', '.conf',
        '.py', '.java', '.c', '.cpp', '.h', '.hpp', '.cs', '.php', '.rb', '.go',
        '.rs', '.swift', '.kt', '.scala', '.sql', '.sh', '.bash', '.zsh', '.ps1',
        '.bat', '.cmd', '.vue', '.svelte', '.scss', '.sass', '.less', '.styl'
    }
    
    # Binary file signatures (first few bytes)
    BINARY_SIGNATURES = [
        b'\x89PNG', b'\xFF\xD8', b'%PDF', b'GIF', b'RIFF', b'PK\x03\x04',
        b'\x7FELF', b'MZ', b'\xCA\xFE\xBA\xBE', b'\xBA\xBE\xCA\xFE'
    ]
    
    def __init__(
        self,
        source_root: str,
        dest_root: str,
        ignore_dirs: Optional[List[str]] = None,
        file_types: Optional[List[str]] = None
    ):
        """
        Initialize the file handler.
        
        Args:
            source_root: Source directory to traverse
            dest_root: Destination directory for output
            ignore_dirs: List of directory names to skip
            file_types: List of file extensions to include (None = all text files)
        """
        self.source_root = Path(source_root).resolve()
        self.dest_root = Path(dest_root).resolve()
        self.ignore_dirs = set(ignore_dirs or [])
        self.file_types = set(file_types) if file_types else None
        
        self.logger = logging.getLogger(__name__)
    
    def get_files_to_process(self) -> List[Dict]:
        """
        Recursively walk through source directory and collect files to process.
        
        Returns:
            List of dictionaries with file information (source_path, dest_path, relative_path)
        """
        files = []
        
        for root, dirs, filenames in os.walk(self.source_root):
            # Filter out ignored directories (modify dirs in-place to prevent traversal)
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            current_root = Path(root)
            
            for filename in filenames:
                file_path = current_root / filename
                
                # Check if file should be processed
                if self._should_process_file(file_path):
                    relative_path = file_path.relative_to(self.source_root)
                    dest_path = self.dest_root / relative_path
                    
                    files.append({
                        'source_path': file_path,
                        'dest_path': dest_path,
                        'relative_path': relative_path,
                        'filename': filename
                    })
        
        return files
    
    def _should_process_file(self, file_path: Path) -> bool:
        """
        Determine if a file should be processed based on file type and extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file should be processed, False otherwise
        """
        # Check if it's a regular file
        if not file_path.is_file():
            return False
        
        # Get file extension
        extension = file_path.suffix.lower()
        
        # If file_types is specified, only include matching extensions
        if self.file_types is not None:
            # Ensure extensions have leading dot for comparison
            normalized_types = [t if t.startswith('.') else f'.{t}' for t in self.file_types]
            return extension in normalized_types
        
        # Otherwise, intelligently detect text files
        return self._is_text_file(file_path)
    
    def _is_text_file(self, file_path: Path, sample_size: int = 1024) -> bool:
        """
        Intelligently detect if a file is a text file by checking extension and content.
        
        Args:
            file_path: Path to the file
            sample_size: Number of bytes to sample for binary detection
            
        Returns:
            True if the file appears to be a text file, False otherwise
        """
        # First check extension
        if file_path.suffix.lower() in self.TEXT_EXTENSIONS:
            return True
        
        # Check file size - empty files are considered text
        if file_path.stat().st_size == 0:
            return True
        
        # Read a sample and check for binary content
        try:
            with open(file_path, 'rb') as f:
                sample = f.read(sample_size)
                
                # Check for binary signatures
                for signature in self.BINARY_SIGNATURES:
                    if sample.startswith(signature):
                        return False
                
                # Check for null bytes (common in binary files)
                if b'\x00' in sample:
                    return False
                
                # Try to decode as UTF-8
                try:
                    sample.decode('utf-8')
                    return True
                except UnicodeDecodeError:
                    # Try common text encodings
                    try:
                        sample.decode('latin-1')
                        return True
                    except UnicodeDecodeError:
                        return False
                        
        except (IOError, OSError) as e:
            self.logger.debug(f"Error reading file {file_path}: {e}")
            return False
    
    def read_file(self, file_path: Path) -> Tuple[Optional[str], Optional[str]]:
        """
        Read a file with automatic encoding detection.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            Tuple of (content, encoding) or (None, None) if reading failed
        """
        # Try UTF-8 first (most common)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return content, 'utf-8'
        except UnicodeDecodeError:
            pass
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            return None, None
        
        # Detect encoding using chardet
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                
            # Use chardet to detect encoding
            detection = chardet.detect(raw_data)
            encoding = detection.get('encoding', 'utf-8')
            
            # Fallback to latin-1 if detection fails
            if encoding is None or encoding.lower() == 'ascii':
                encoding = 'latin-1'
            
            # Try to decode with detected encoding
            try:
                content = raw_data.decode(encoding)
                return content, encoding
            except UnicodeDecodeError:
                # Final fallback to latin-1 (should never fail)
                content = raw_data.decode('latin-1', errors='replace')
                return content, 'latin-1'
                
        except Exception as e:
            self.logger.error(f"Error detecting encoding for {file_path}: {e}")
            return None, None
    
    def write_file(
        self,
        file_path: Path,
        content: str,
        encoding: str,
        preserve_timestamps: bool = False,
        source_path: Optional[Path] = None
    ) -> bool:
        """
        Write content to a file, creating directories as needed.
        
        Args:
            file_path: Path where to write the file
            content: Content to write
            encoding: Character encoding to use
            preserve_timestamps: If True, preserve timestamps from source file
            source_path: Source file path (required if preserve_timestamps is True)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the file
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            # Preserve timestamps if requested
            if preserve_timestamps and source_path and source_path.exists():
                try:
                    stat = source_path.stat()
                    os.utime(file_path, (stat.st_atime, stat.st_mtime))
                except Exception as e:
                    self.logger.debug(f"Could not preserve timestamps for {file_path}: {e}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error writing file {file_path}: {e}")
            return False