"""
Unit tests for the ReplacementEngine.
"""

import unittest
from batch_replace.replacement_engine import ReplacementEngine


class TestReplacementEngine(unittest.TestCase):
    """Test cases for ReplacementEngine class."""
    
    def test_string_replacement_single(self):
        """Test single string replacement."""
        engine = ReplacementEngine("Hello", "Hi", use_regex=False)
        content = "Hello world"
        result, count = engine.apply(content)
        self.assertEqual(result, "Hi world")
        self.assertEqual(count, 1)
    
    def test_string_replacement_multiple(self):
        """Test multiple string replacements."""
        engine = ReplacementEngine("Hello", "Hi", use_regex=False)
        content = "Hello world, Hello again"
        result, count = engine.apply(content)
        self.assertEqual(result, "Hi world, Hi again")
        self.assertEqual(count, 2)
    
    def test_string_replacement_no_match(self):
        """Test when pattern doesn't match."""
        engine = ReplacementEngine("Goodbye", "Hi", use_regex=False)
        content = "Hello world"
        result, count = engine.apply(content)
        self.assertEqual(result, "Hello world")
        self.assertEqual(count, 0)
    
    def test_regex_replacement_basic(self):
        """Test basic regex replacement."""
        engine = ReplacementEngine(r"\d+", "[NUMBER]", use_regex=True)
        content = "Item 123 costs $456"
        result, count = engine.apply(content)
        self.assertEqual(result, "Item [NUMBER] costs $[NUMBER]")
        self.assertEqual(count, 2)
    
    def test_regex_replacement_with_groups(self):
        """Test regex replacement with capture groups."""
        engine = ReplacementEngine(r"(\d{3})-(\d{4})", r"(\1) \2", use_regex=True)
        content = "Call 555-1234 now"
        result, count = engine.apply(content)
        self.assertEqual(result, "Call (555) 1234 now")
        self.assertEqual(count, 1)
    
    def test_regex_invalid_pattern(self):
        """Test handling of invalid regex pattern."""
        with self.assertRaises(ValueError):
            ReplacementEngine(r"[invalid", "", use_regex=True)
    
    def test_empty_content(self):
        """Test with empty content."""
        engine = ReplacementEngine("Hello", "Hi", use_regex=False)
        result, count = engine.apply("")
        self.assertEqual(result, "")
        self.assertEqual(count, 0)


if __name__ == '__main__':
    unittest.main()