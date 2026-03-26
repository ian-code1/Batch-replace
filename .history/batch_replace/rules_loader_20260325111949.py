"""
Loader for replacement rules from JSON and YAML files.
Handles parsing and validation of rule files and environment configurations.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging


class RulesLoader:
    """
    Loads and validates replacement rules from configuration files.
    Supports both JSON and YAML formats.
    """
    
    @staticmethod
    def load_rules(rules_file: str) -> List[Dict[str, Any]]:
        """
        Load replacement rules from a JSON or YAML file.
        
        Args:
            rules_file: Path to the rules file
            
        Returns:
            List of rule dictionaries with pattern, replace, and optional regex flag
            
        Raises:
            ValueError: If the file format is invalid or rules are malformed
        """
        logger = logging.getLogger(__name__)
        file_path = Path(rules_file)
        
        if not file_path.exists():
            raise ValueError(f"Rules file not found: {rules_file}")
        
        # Determine file type by extension
        extension = file_path.suffix.lower()
        
        data = None
        if extension in ['.json']:
            data = RulesLoader._load_json(file_path)
        elif extension in ['.yaml', '.yml']:
            data = RulesLoader._load_yaml(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}. Use .json, .yaml, or .yml")
        
        # Validate structure
        if isinstance(data, dict):
            # Check for 'rules' key
            if 'rules' in data:
                rules = data['rules']
            else:
                rules = [data]  # Single rule object
        elif isinstance(data, list):
            rules = data
        else:
            raise ValueError("Rules file must contain a list of rules or an object with a 'rules' array")
        
        # Validate each rule
        validated_rules = []
        for idx, rule in enumerate(rules):
            if not isinstance(rule, dict):
                raise ValueError(f"Rule {idx} is not a dictionary")
            
            if 'pattern' not in rule:
                raise ValueError(f"Rule {idx} missing 'pattern' field")
            
            if 'replace' not in rule:
                raise ValueError(f"Rule {idx} missing 'replace' field")
            
            validated_rule = {
                'pattern': rule['pattern'],
                'replace': rule['replace'],
                'regex': rule.get('regex', False)  # Default to exact match
            }
            
            validated_rules.append(validated_rule)
            logger.debug(f"Loaded rule: {validated_rule}")
        
        return validated_rules
    
    @staticmethod
    def load_env_config(config_file: str, environment: str) -> Dict[str, str]:
        """
        Load environment-specific configuration.
        
        Args:
            config_file: Path to the environment config file (JSON)
            environment: Environment name (dev, prod, staging, etc.)
            
        Returns:
            Dictionary of variable mappings for the specified environment
            
        Raises:
            ValueError: If the config file is invalid or environment not found
        """
        logger = logging.getLogger(__name__)
        file_path = Path(config_file)
        
        if not file_path.exists():
            raise ValueError(f"Environment config file not found: {config_file}")
        
        # Load JSON config
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in environment config: {e}")
        
        # Check structure
        if not isinstance(config, dict):
            raise ValueError("Environment config must be a JSON object")
        
        # Check for environments key
        if 'environments' in config:
            env_config = config['environments']
            if not isinstance(env_config, dict):
                raise ValueError("'environments' must be an object")
        else:
            # Assume top-level keys are environment names
            env_config = config
        
        # Find the specified environment
        if environment not in env_config:
            available = ', '.join(env_config.keys())
            raise ValueError(f"Environment '{environment}' not found. Available: {available}")
        
        env_vars = env_config[environment]
        
        if not isinstance(env_vars, dict):
            raise ValueError(f"Environment '{environment}' must be an object")
        
        logger.debug(f"Loaded {len(env_vars)} variables for environment '{environment}'")
        return env_vars
    
    @staticmethod
    def _load_json(file_path: Path) -> Any:
        """Load and parse JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {file_path}: {e}")
    
    @staticmethod
    def _load_yaml(file_path: Path) -> Any:
        """Load and parse YAML file."""
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML is required to load YAML files. Install with: pip install pyyaml")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {file_path}: {e}")