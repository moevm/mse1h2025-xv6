import unittest
from unittest.mock import patch, MagicMock
from scripts.run_tests import main as run_tests_main


class TestLabRunner(unittest.TestCase):
    @patch('subprocess.Popen')
    @patch('os.chdir')
    def test_successful_execution(self, mock_chdir, mock_popen):
        """Тест успешного выполнения"""
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc

        with patch('sys.exit') as mock_exit:
            run_tests_main()
            mock_exit.assert_called_with(0)
