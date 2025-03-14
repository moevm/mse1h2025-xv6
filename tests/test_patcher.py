import unittest
import tempfile
import os
from unittest.mock import patch
from src.patcher import apply_patch


class TestPatcher(unittest.TestCase):
    def setUp(self):
        # Создание тестового патча и файлов
        self.temp_dir = tempfile.TemporaryDirectory()
        self.patch_content = """--- a/test.txt\n+++ b/test.txt\n@@ -1 +1 @@\n-original\n+patched"""

        self.patch_file = os.path.join(self.temp_dir.name, 'test.patch')
        with open(self.patch_file, 'w') as f:
            f.write(self.patch_content)

    def test_git_apply_success(self):
        """Тест успешного применения git патча"""
        test_file = os.path.join(self.temp_dir.name, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('original')

        apply_patch(self.patch_file, self.temp_dir.name)

        with open(test_file) as f:
            self.assertEqual(f.read().strip(), 'patched')

    @patch('subprocess.run')
    def test_patch_conflict(self, mock_run):
        """Тест конфликта при применении патча"""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = 'patch conflict'

        with self.assertRaises(RuntimeError) as cm:
            apply_patch('invalid.patch', '/fake/dir')
        self.assertIn('Conflict detected', str(cm.exception))