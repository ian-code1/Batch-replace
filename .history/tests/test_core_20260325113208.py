"""
Unit tests for the core BatchReplacer functionality.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import json

from batch_replace.core import BatchReplacer


class TestBatchReplacer(unittest.TestCase):
    """Test cases for BatchReplacer class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directories
        self.source_dir = tempfile.mkdtemp()
        self.dest_dir = tempfile.mkdtemp()
        
        # Create test files
        self.create_test_files()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.source_dir)
        shutil.rmtree(self.dest_dir)
    
    def create_test_files(self):
        """Create test files with sample content."""
        # Create a simple text file
        test_file = Path(self.source_dir) / "test.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("Hello world\n")
            f.write("Hello again\n")
            f.write("Goodbye\n")
        
        # Create a nested directory with file
        nested_dir = Path(self.source_dir) / "nested"
        nested_dir.mkdir()
        nested_file = nested_dir / "test.html"
        with open(nested_file, 'w', encoding='utf-8') as f:
            f.write("<div>Hello world</div>\n")
            f.write("<p>Hello again</p>\n")
        
        # Create a file that should be ignored (binary)
        binary_file = Path(self.source_dir) / "test.bin"
        with open(binary_file, 'wb') as f:
            f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR')
    
    def test_single_string_replacement(self):
        """Test basic string replacement."""
        replacer = BatchReplacer(
            source_root=self.source_dir,
            dest_root=self.dest_dir,
            pattern="Hello",
            replace="Hi",
            use_regex=False
        )
        
        success = replacer.run()
        self.assertTrue(success)
        
        # Check the output file
        output_file = Path(self.dest_dir) / "test.txt"
        self.assertTrue(output_file.exists())
        
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("Hi world", content)
            self.assertIn("Hi again", content)
            self.assertNotIn("Hello", content)
    
    def test_regex_replacement(self):
        """Test regex-based replacement."""
        replacer = BatchReplacer(
            source_root=self.source_dir,
            dest_root=self.dest_dir,
            pattern=r"Hell\w+",
            replace="Hi",
            use_regex=True
        )
        
        success = replacer.run()
        self.assertTrue(success)
        
        output_file = Path(self.dest_dir) / "test.txt"
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("Hi world", content)
            self.assertIn("Hi again", content)
    
    def test_file_type_filtering(self):
        """Test file type filtering."""
        replacer = BatchReplacer(
            source_root=self.source_dir,
            dest_root=self.dest_dir,
            pattern="Hello",
            replace="Hi",
            file_types=[".html"]
        )
        
        success = replacer.run()
        self.assertTrue(success)
        
        # HTML file should be processed
        html_file = Path(self.dest_dir) / "nested" / "test.html"
        self.assertTrue(html_file.exists())
        
        # Text file should not be processed
        txt_file = Path(self.dest_dir) / "test.txt"
        self.assertFalse(txt_file.exists())
    
    def test_dry_run(self):
        """Test dry run mode."""
        replacer = BatchReplacer(
            source_root=self.source_dir,
            dest_root=self.dest_dir,
            pattern="Hello",
            replace="Hi",
            dry_run=True
        )
        
        success = replacer.run()
        self.assertTrue(success)
        
        # Destination directory should not exist (or be empty)
        self.assertFalse(Path(self.dest_dir).exists() or list(Path(self.dest_dir).iterdir()))
    
    def test_ignore_dirs(self):
        """Test directory ignoring."""
        # Create a directory that should be ignored
        ignored_dir = Path(self.source_dir) / "node_modules"
        ignored_dir.mkdir()
        ignored_file = ignored_dir / "ignore.txt"
        with open(ignored_file, 'w', encoding='utf-8') as f:
            f.write("Should be ignored\n")
        
        replacer = BatchReplacer(
            source_root=self.source_dir,
            dest_root=self.dest_dir,
            pattern="Hello",
            replace="Hi",
            ignore_dirs=["node_modules"]
        )
        
        success = replacer.run()
        self.assertTrue(success)
        
        # Ignored file should not be in destination
        ignored_output = Path(self.dest_dir) / "node_modules" / "ignore.txt"
        self.assertFalse(ignored_output.exists())


if __name__ == '__main__':
    unittest.main()