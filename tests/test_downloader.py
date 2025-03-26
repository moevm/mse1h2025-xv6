import unittest
import tempfile
import os
import zipfile
from pathlib import Path
from unittest.mock import patch
from scripts.load import extract_archive

class TestDownloader(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.extract_dir = tempfile.TemporaryDirectory()
        self.valid_zip = os.path.join(self.temp_dir.name, 'test.zip')
        with zipfile.ZipFile(self.valid_zip, 'w') as zf:
            zf.writestr('test.txt', 'content')

    def tearDown(self):
        self.temp_dir.cleanup()
        self.extract_dir.cleanup()

    def test_extract_valid_archive(self):
        """Тест успешного разархивирования"""
        extract_path = extract_archive(Path(self.valid_zip), Path(self.extract_dir.name))
        self.assertTrue((Path(extract_path) / 'test.txt').exists())

    @patch('sys.exit')
    def test_invalid_archive_format(self, mock_exit):
        """Тест обработки неверного формата архива"""
        extract_archive(Path('invalid.rar'), Path(self.extract_dir.name))
        mock_exit.assert_called_with(1)

    @patch('sys.exit')
    def test_empty_archive(self, mock_exit):
        """Тест пустого архива"""
        empty_zip = os.path.join(self.temp_dir.name, 'empty.zip')
        with zipfile.ZipFile(empty_zip, 'w'):
            pass
        extract_archive(Path(empty_zip), Path(self.extract_dir.name))
        mock_exit.assert_called_with(1)