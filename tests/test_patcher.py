import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from scripts.load import apply_patch


class TestPatcher(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.patch_content = """--- a/test.txt\n+++ b/test.txt\n@@ -1 +1 @@\n-original\n+patched"""
        self.patch_file = os.path.join(self.temp_dir.name, 'test.patch')
        with open(self.patch_file, 'w') as f:
            f.write(self.patch_content)

    def test_apply_patch_success(self):
        """Тест успешного применения патча"""
        test_file = os.path.join(self.temp_dir.name, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('original')

        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            result = apply_patch(Path(self.patch_file), Path(self.temp_dir.name))
            self.assertTrue(result)

    @patch('subprocess.run')
    def test_patch_failure(self, mock_run):
        """Тест ошибки при применении патча"""
        mock_run.return_value.returncode = 1
        result = apply_patch(Path('invalid.patch'), Path('/fake/dir'))
        self.assertFalse(result)