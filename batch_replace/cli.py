#!/usr/bin/env python3
"""
Command-line interface for the batch search-and-replace tool.
Handles argument parsing, logging setup, and orchestrating the replacement process.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import List, Optional
import logging

from batch_replace.core import BatchReplacer
from batch_replace.logger import setup_logging, LogColors
from batch_replace.utils import validate_paths


def parse_arguments(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Args:
        args: Command line arguments (defaults to sys.argv[1:])
        
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Batch search and replace tool for text files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  %(prog)s --source ./src --destination ./output --pattern "old" --replace "new"
  
  # With file type filter
  %(prog)s --source ./src --destination ./output --pattern "old" --replace "new" --file-types .html,.js,.css
  
  # Dry run to preview changes
  %(prog)s --source ./src --destination ./output --pattern "old" --replace "new" --dry-run
  
  # Using rules file
  %(prog)s --source ./src --destination ./output --rules-file rules.json
  
  # With environment config
  %(prog)s --source ./src --destination ./output --rules-file rules.json --env dev --env-config env_config.json
  
  # Verbose mode with ignored folders
  %(prog)s --source ./src --destination ./output --pattern "old" --replace "new" --verbose --ignore-dirs .git,node_modules,dist
        """
    )
    
    # Required arguments
    parser.add_argument(
        "--source",
        required=True,
        help="Source folder to process"
    )
    
    parser.add_argument(
        "--destination",
        required=True,
        help="Destination folder for modified copies"
    )
    
    # Search/replace arguments
    parser.add_argument(
        "--pattern",
        help="String or regex pattern to search for (if not using --rules-file)"
    )
    
    parser.add_argument(
        "--replace",
        help="Replacement string (if not using --rules-file)"
    )
    
    # Rules file
    parser.add_argument(
        "--rules-file",
        help="JSON or YAML file containing multiple replacement rules"
    )
    
    # Environment configuration
    parser.add_argument(
        "--env",
        help="Environment name (dev, prod, staging) for environment-specific replacements"
    )
    
    parser.add_argument(
        "--env-config",
        help="JSON file containing environment-specific replacement mappings"
    )
    
    # File filtering
    parser.add_argument(
        "--file-types",
        help="Comma-separated list of file extensions to process (e.g., .html,.js,.css)"
    )
    
    parser.add_argument(
        "--ignore-dirs",
        default=".git,node_modules,__pycache__,dist,build,.idea,.vscode",
        help="Comma-separated list of directory names to ignore (default: .git,node_modules,__pycache__,dist,build,.idea,.vscode)"
    )
    
    # Mode flags
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files"
    )
    
    parser.add_argument(
        "--regex",
        action="store_true",
        help="Treat pattern as regular expression (default: exact string match)"
    )
    
    parser.add_argument(
        "--preserve-timestamps",
        action="store_true",
        help="Preserve original file timestamps in the destination folder"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging output"
    )
    
    # Logging
    parser.add_argument(
        "--log-file",
        help="Path to log file (default: batch_replace.log)"
    )
    
    # Validation
    if args is None:
        args = sys.argv[1:]
    
    parsed_args = parser.parse_args(args)
    
    # Validate arguments
    if not parsed_args.pattern and not parsed_args.rules_file:
        parser.error("Either --pattern or --rules-file must be provided")
    
    if parsed_args.pattern and parsed_args.replace is None:
        parser.error("--replace is required when using --pattern")
    
    if parsed_args.rules_file and (parsed_args.pattern or parsed_args.replace):
        parser.error("Cannot use --pattern/--replace with --rules-file")
    
    if parsed_args.env and not parsed_args.env_config:
        parser.error("--env-config is required when using --env")
    
    return parsed_args


def main() -> int:
    """
    Main entry point for the batch search-and-replace tool.
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Setup logging
        log_file = args.log_file or "batch_replace.log"
        logger = setup_logging(
            verbose=args.verbose,
            log_file=log_file,
            console_output=True
        )
        
        logger.info(f"{LogColors.BOLD}Batch Search and Replace Tool v1.0.0{LogColors.END}")
        logger.info(f"Source: {args.source}")
        logger.info(f"Destination: {args.destination}")
        
        if args.dry_run:
            logger.warning(f"{LogColors.WARNING}DRY RUN MODE - No files will be written{LogColors.END}")
        
        # Validate paths
        if not validate_paths(args.source, args.destination, args.dry_run):
            return 1
        
        # Parse file types
        file_types = None
        if args.file_types:
            file_types = [ft.strip() for ft in args.file_types.split(",")]
        
        # Parse ignore directories
        ignore_dirs = [d.strip() for d in args.ignore_dirs.split(",")]
        
        # Create and run the batch replacer
        replacer = BatchReplacer(
            source_root=args.source,
            dest_root=args.destination,
            pattern=args.pattern,
            replace=args.replace,
            rules_file=args.rules_file,
            use_regex=args.regex,
            file_types=file_types,
            ignore_dirs=ignore_dirs,
            env=args.env,
            env_config_file=args.env_config,
            dry_run=args.dry_run,
            preserve_timestamps=args.preserve_timestamps,
            verbose=args.verbose
        )
        
        # Execute the replacement process
        success = replacer.run()
        
        if success:
            logger.info(f"{LogColors.SUCCESS}✓ Batch replacement completed successfully{LogColors.END}")
            return 0
        else:
            logger.error(f"{LogColors.ERROR}✗ Batch replacement failed{LogColors.END}")
            return 1
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if hasattr(e, '__traceback__'):
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())