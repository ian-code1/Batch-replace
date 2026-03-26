"""
Core orchestration logic for the batch search-and-replace tool.
Coordinates file discovery, replacement operations, and logging.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Dict, Tuple
import logging
from datetime import datetime

from batch_replace.file_handler import FileHandler
from batch_replace.replacement_engine import ReplacementEngine
from batch_replace.rules_loader import RulesLoader
from batch_replace.logger import LogColors


class BatchReplacer:
    """
    Main orchestrator for batch search and replace operations.
    Handles file traversal, applies replacements, and manages the process flow.
    """
    
    def __init__(
        self,
        source_root: str,
        dest_root: str,
        pattern: Optional[str] = None,
        replace: Optional[str] = None,
        rules_file: Optional[str] = None,
        use_regex: bool = False,
        file_types: Optional[List[str]] = None,
        ignore_dirs: Optional[List[str]] = None,
        env: Optional[str] = None,
        env_config_file: Optional[str] = None,
        dry_run: bool = False,
        preserve_timestamps: bool = False,
        verbose: bool = False
    ):
        """
        Initialize the batch replacer.
        
        Args:
            source_root: Source directory to process
            dest_root: Destination directory for modified files
            pattern: Search pattern (string or regex)
            replace: Replacement string
            rules_file: Path to rules file (JSON/YAML)
            use_regex: Whether to treat pattern as regex
            file_types: List of file extensions to process (None = all text files)
            ignore_dirs: List of directory names to skip
            env: Environment name for variable substitution
            env_config_file: Path to environment config file
            dry_run: If True, preview changes without writing
            preserve_timestamps: If True, preserve original file timestamps
            verbose: Enable verbose logging
        """
        self.source_root = Path(source_root).resolve()
        self.dest_root = Path(dest_root).resolve()
        self.use_regex = use_regex
        self.file_types = file_types
        self.ignore_dirs = ignore_dirs or ['.git', 'node_modules', '__pycache__']
        self.dry_run = dry_run
        self.preserve_timestamps = preserve_timestamps
        self.verbose = verbose
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.file_handler = FileHandler(
            source_root=str(self.source_root),
            dest_root=str(self.dest_root),
            ignore_dirs=self.ignore_dirs,
            file_types=self.file_types
        )
        
        # Load replacement rules
        self.rules = []
        self.env_vars = {}
        
        if rules_file:
            # Load from rules file
            self.rules = RulesLoader.load_rules(rules_file)
            self.logger.info(f"Loaded {len(self.rules)} replacement rules from {rules_file}")
        elif pattern is not None and replace is not None:
            # Single rule
            self.rules = [{
                'pattern': pattern,
                'replace': replace,
                'regex': use_regex
            }]
            self.logger.info(f"Using single rule: '{pattern}' -> '{replace}' (regex={use_regex})")
        
        # Load environment configuration if provided
        if env and env_config_file:
            self.env_vars = RulesLoader.load_env_config(env_config_file, env)
            self.logger.info(f"Loaded environment '{env}' configuration from {env_config_file}")
            self.logger.debug(f"Environment variables: {self.env_vars}")
    
    def run(self) -> bool:
        """
        Execute the batch replacement process.
        
        Returns:
            True if successful, False otherwise
        """
        self.logger.info("=" * 60)
        self.logger.info(f"Starting batch replacement at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 60)
        
        if self.dry_run:
            self.logger.warning(f"{LogColors.WARNING}DRY RUN MODE - No files will be written{LogColors.END}")
        
        # Validate source directory
        if not self.dry_run:
            if not self.source_root.exists():
                self.logger.error(f"Source directory does not exist: {self.source_root}")
                return False
        
        if not self.source_root.is_dir():
            self.logger.error(f"Source path is not a directory: {self.source_root}")
            return False
        
        # Create destination directory if it doesn't exist
        if not self.dry_run and not self.dest_root.exists():
            try:
                self.dest_root.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created destination directory: {self.dest_root}")
            except Exception as e:
                self.logger.error(f"Failed to create destination directory: {e}")
                return False
        
        # Collect files to process
        self.logger.info("Scanning for files to process...")
        files_to_process = self.file_handler.get_files_to_process()
        
        if not files_to_process:
            self.logger.warning("No files found matching the criteria")
            return True
        
        self.logger.info(f"Found {len(files_to_process)} file(s) to process")
        
        # Process each file
        stats = {
            'total': len(files_to_process),
            'processed': 0,
            'modified': 0,
            'skipped': 0,
            'errors': 0,
            'total_replacements': 0
        }
        
        for idx, file_info in enumerate(files_to_process, 1):
            self.logger.info(f"\n{LogColors.BOLD}[{idx}/{stats['total']}] Processing: {file_info['relative_path']}{LogColors.END}")
            
            try:
                result = self._process_file(file_info)
                
                if result['processed']:
                    stats['processed'] += 1
                    if result['modified']:
                        stats['modified'] += 1
                        stats['total_replacements'] += result['replacements']
                        self.logger.info(
                            f"{LogColors.SUCCESS}  ✓ Modified - {result['replacements']} replacement(s){LogColors.END}"
                        )
                    else:
                        self.logger.info(f"  - No changes (file copied as-is)")
                else:
                    stats['skipped'] += 1
                    
            except Exception as e:
                stats['errors'] += 1
                self.logger.error(f"{LogColors.ERROR}  ✗ Error: {e}{LogColors.END}")
                if self.verbose:
                    import traceback
                    traceback.print_exc()
        
        # Print summary
        self._print_summary(stats)
        
        return stats['errors'] == 0
    
    def _process_file(self, file_info: Dict) -> Dict:
        """
        Process a single file: read, apply replacements, and write.
        
        Args:
            file_info: Dictionary with file information
            
        Returns:
            Dictionary with processing results
        """
        result = {
            'processed': False,
            'modified': False,
            'replacements': 0
        }
        
        source_path = file_info['source_path']
        dest_path = file_info['dest_path']
        
        # Read file content
        content, encoding = self.file_handler.read_file(source_path)
        if content is None:
            self.logger.warning(f"  Skipping file (could not read): {source_path}")
            return result
        
        original_content = content
        
        # Apply all replacement rules
        total_replacements = 0
        for rule in self.rules:
            # Apply environment variable substitution to replacement string
            replace_text = self._substitute_env_vars(rule['replace'])
            
            # Create engine for this rule
            engine = ReplacementEngine(
                pattern=rule['pattern'],
                replace=replace_text,
                use_regex=rule.get('regex', self.use_regex)
            )
            
            # Apply replacement
            content, count = engine.apply(content)
            total_replacements += count
            
            if count > 0 and self.verbose:
                self.logger.debug(f"    Rule '{rule['pattern']}' -> '{replace_text}': {count} replacement(s)")
        
        # Check if content changed
        if content != original_content:
            result['modified'] = True
            result['replacements'] = total_replacements
            
            if self.verbose:
                self.logger.debug(f"    Changes detected: {total_replacements} replacement(s)")
        
        # Write file (if not dry run)
        if not self.dry_run:
            success = self.file_handler.write_file(
                dest_path,
                content,
                encoding,
                preserve_timestamps=self.preserve_timestamps,
                source_path=source_path if self.preserve_timestamps else None
            )
            
            if not success:
                self.logger.error(f"  Failed to write file: {dest_path}")
                return result
        
        result['processed'] = True
        return result
    
    def _substitute_env_vars(self, text: str) -> str:
        """
        Substitute environment variables in a string.
        
        Args:
            text: String that may contain ${VAR} placeholders
            
        Returns:
            String with environment variables substituted
        """
        if not self.env_vars:
            return text
        
        result = text
        for key, value in self.env_vars.items():
            placeholder = f"${{{key}}}"
            if placeholder in result:
                result = result.replace(placeholder, value)
                if self.verbose:
                    self.logger.debug(f"    Substituted {placeholder} -> {value}")
        
        return result
    
    def _print_summary(self, stats: Dict) -> None:
        """
        Print processing summary.
        
        Args:
            stats: Dictionary with processing statistics
        """
        self.logger.info("\n" + "=" * 60)
        self.logger.info(f"{LogColors.BOLD}SUMMARY{LogColors.END}")
        self.logger.info("=" * 60)
        self.logger.info(f"Total files found:     {stats['total']}")
        self.logger.info(f"Files processed:       {stats['processed']}")
        self.logger.info(f"Files modified:        {stats['modified']}")
        self.logger.info(f"Files skipped:         {stats['skipped']}")
        self.logger.info(f"Files with errors:     {stats['errors']}")
        self.logger.info(f"Total replacements:    {stats['total_replacements']}")
        
        if self.dry_run:
            self.logger.warning(f"\n{LogColors.WARNING}DRY RUN - No files were actually modified{LogColors.END}")
        
        self.logger.info("=" * 60)