"""
Unit tests for the FileHandler.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import os

from batch_replace.file_handler import FileHandler


class TestFileHandler(unittest.TestCase):
    """Test cases for FileHandler class."""
    
    def setUp(self):
        """Set up test environment."""
        self.source_dir = tempfile.mkdtemp()
        self.dest_dir = tempfile.mkdtemp()
        
        # Create test files
        self.create_test_files()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.source_dir)
        shutil.rmtree(self.dest_dir)
    
    def create_test_files(self):
        """Create test files with various types."""
        # Text files
        text_file = Path(self.source_dir) / "test.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write("This is a text file\n")
        
        # HTML file
        html_file = Path(self.source_dir) / "index.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write("<html><body>Test</body></html>\n")
        
        # Nested directory
        nested_dir = Path(self.source_dir) / "subdir"
        nested_dir.mkdir()
        nested_file = nested_dir / "nested.txt"
        with open(nested_file, 'w', encoding='utf-8') as f:
            f.write("Nested file\n")
        
        # Binary file
        binary_file = Path(self.source_dir) / "test.png"
        with open(binary_file, 'wb') as f:
            f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR')
        
        # Directory to ignore
        ignore_dir = Path(self.source_dir) / "node_modules"
        ignore_dir.mkdir()
        ignore_file = ignore_dir / "ignore.txt"
        with open(ignore_file, 'w', encoding='utf-8') as f:
            f.write("Should be ignored\n")
    
    def test_get_files_to_process_all_text(self):
        """Test file collection for all text files."""
        handler = FileHandler(
            source_root=self.source_dir,
            dest_root=self.dest_dir,
            ignore_dirs=["node_modules"]
        )
        
        files = handler.get_files_to_process()
        
        # Should find 3 text files (test.txt, index.html, nested.txt)
        self.assertEqual(len(files), 3)
        
        # Verify paths
        relative_paths = [f['relative_path'].as_posix() for f in files]
        self.assertIn("test.txt", relative_paths)
        self.assertIn("index.html", relative_paths)
        self.assertIn("subdir/nested.txt", relative_paths)
    
    def test_get_files_to_process_filtered(self):
        """Test file collection with extension filtering."""
        handler = FileHandler(
            source_root=self.source_dir,
            dest_root=self.dest_dir,
            ignore_dirs=["node_modules"],
            file_types=[".html"]
        )
        
        files = handler.get_files_to_process()
        
        # Should only find HTML files
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]['filename'], "index.html")
    
    def test_is_text_file_detection(self):
        """Test text file detection."""
        handler = FileHandler(
            source_root=self.source_dir,
            dest_root=self.dest_dir
        )
        
        # Text files should be detected as text
        text_file = Path(self.source_dir) / "test.txt"
        self.assertTrue(handler._is_text_file(text_file))
        
        # Binary file should be detected as binary
        binary_file = Path(self.source_dir) / "test.png"
        self.assertFalse(handler._is_text_file(binary_file))
    
    def test_read_file_utf8(self):
        """Test reading UTF-8 encoded file."""
        handler = FileHandler(
            source_root=self.source_dir,
            dest_root=self.dest_dir
        )
        
        text_file = Path(self.source_dir) / "test.txt"
        content, encoding = handler.read_file(text_file)
        
        self.assertIsNotNone(content)
        self.assertEqual(encoding, 'utf-8')
        self.assertIn("text file", content)
    
    def test_write_file(self):
        """Test writing file with directory creation."""
        handler = FileHandler(
            source_root=self.source_dir,
            dest_root=self.dest_dir
        )
        
        dest_file = Path(self.dest_dir) / "new" / "file.txt"
        success = handler.write_file(
            dest_file,
            "Test content",
            "utf-8"
        )
        
        self.assertTrue(success)
        self.assertTrue(dest_file.exists())
        
        with open(dest_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertEqual(content, "Test content")


if __name__ == '__main__':
    unittest.main()