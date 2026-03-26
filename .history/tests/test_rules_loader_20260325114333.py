"""
Unit tests for the RulesLoader.
"""

import unittest
import tempfile
import json
from pathlib import Path

from batch_replace.rules_loader import RulesLoader


class TestRulesLoader(unittest.TestCase):
    """Test cases for RulesLoader class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_json_file(self, data):
        """Create a temporary JSON file."""
        file_path = Path(self.temp_dir) / "rules.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return file_path
    
    def test_load_rules_single(self):
        """Test loading a single rule from JSON."""
        rules_data = {
            "pattern": "Hello",
            "replace": "Hi"
        }
        file_path = self.create_json_file(rules_data)
        
        rules = RulesLoader.load_rules(str(file_path))
        
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0]['pattern'], "Hello")
        self.assertEqual(rules[0]['replace'], "Hi")
        self.assertEqual(rules[0]['regex'], False)
    
    def test_load_rules_multiple(self):
        """Test loading multiple rules from JSON."""
        rules_data = {
            "rules": [
                {"pattern": "Hello", "replace": "Hi", "regex": False},
                {"pattern": "\\d+", "replace": "[NUMBER]", "regex": True}
            ]
        }
        file_path = self.create_json_file(rules_data)
        
        rules = RulesLoader.load_rules(str(file_path))
        
        self.assertEqual(len(rules), 2)
        self.assertEqual(rules[0]['pattern'], "Hello")
        self.assertEqual(rules[1]['regex'], True)
    
    def test_load_rules_list_format(self):
        """Test loading rules from list format."""
        rules_data = [
            {"pattern": "Hello", "replace": "Hi"},
            {"pattern": "World", "replace": "Earth"}
        ]
        file_path = self.create_json_file(rules_data)
        
        rules = RulesLoader.load_rules(str(file_path))
        
        self.assertEqual(len(rules), 2)
    
    def test_load_rules_invalid(self):
        """Test loading invalid rules."""
        rules_data = {"invalid": "format"}
        file_path = self.create_json_file(rules_data)
        
        with self.assertRaises(ValueError):
            RulesLoader.load_rules(str(file_path))
    
    def test_load_env_config(self):
        """Test loading environment configuration."""
        config_data = {
            "environments": {
                "dev": {
                    "API_URL": "http://localhost:8000",
                    "DB_HOST": "localhost"
                },
                "prod": {
                    "API_URL": "https://api.example.com",
                    "DB_HOST": "prod-db.example.com"
                }
            }
        }
        
        config_file = Path(self.temp_dir) / "env_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f)
        
        env_vars = RulesLoader.load_env_config(str(config_file), "dev")
        
        self.assertEqual(env_vars["API_URL"], "http://localhost:8000")
        self.assertEqual(env_vars["DB_HOST"], "localhost")
    
    def test_load_env_config_missing_env(self):
        """Test loading environment config with missing environment."""
        config_data = {
            "environments": {
                "prod": {"API_URL": "https://api.example.com"}
            }
        }
        
        config_file = Path(self.temp_dir) / "env_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f)
        
        with self.assertRaises(ValueError):
            RulesLoader.load_env_config(str(config_file), "dev")


if __name__ == '__main__':
    unittest.main()