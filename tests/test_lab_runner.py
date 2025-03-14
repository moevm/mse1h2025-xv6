import unittest
import tempfile
import os
from unittest.mock import patch
from src.lab_runner import run_lab


class TestLabRunner(unittest.TestCase):
    def test_successful_execution(self):
        """Тест успешного выполнения команды"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'log.txt')
            result = run_lab('echo "Success"', 10, log_file)

            self.assertEqual(result['status'], 'completed')
            self.assertEqual(result['returncode'], 0)
            with open(log_file) as f:
                self.assertIn('Success', f.read())

    def test_timeout_handling(self):
        """Тест обработки таймаута"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'log.txt')
            result = run_lab('sleep 5', 1, log_file)

            self.assertEqual(result['status'], 'timeout')
            self.assertTrue(os.path.exists(log_file))

    def test_error_logging(self):
        """Тест логирования ошибок"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, 'log.txt')
            run_lab('invalid_command', 10, log_file)

            with open(log_file) as f:
                content = f.read()
                self.assertIn('not found', content)
                self.assertIn('stderr', content)