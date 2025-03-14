import unittest
import tempfile
import os
import zipfile
from unittest.mock import patch
from src.downloader import extract_archive, validate_archive

class TestDownloader(unittest.TestCase):
    def setUp(self):
        # Создание временного архива для тестов
        self.temp_dir = tempfile.TemporaryDirectory()
        self.valid_zip = os.path.join(self.temp_dir.name, 'test.zip')
        with zipfile.ZipFile(self.valid_zip, 'w') as zf:
            zf.writestr('test.txt', 'content')

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_extract_valid_archive(self):
        """Тест успешного разархивирования"""
        extract_path = extract_archive(self.valid_zip)
        self.assertTrue(os.path.exists(os.path.join(extract_path, 'test.txt')))
        self.assertIn('temp_lab_dir', extract_path)

    def test_invalid_archive_format(self):
        """Тест обработки неверного формата архива"""
        with self.assertRaises(ValueError):
            extract_archive('invalid_archive.rar')

    @patch('zipfile.ZipFile.testzip')
    def test_corrupted_archive(self, mock_testzip):
        """Тест поврежденного архива"""
        mock_testzip.return_value = ['corrupted_file.txt']
        with self.assertRaises(RuntimeError):
            validate_archive(self.valid_zip)

    def test_empty_archive(self):
        """Тест пустого архива"""
        empty_zip = os.path.join(self.temp_dir.name, 'empty.zip')
        with zipfile.ZipFile(empty_zip, 'w'):
            pass
        with self.assertRaises(RuntimeError):
            extract_archive(empty_zip)
