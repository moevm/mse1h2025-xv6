import unittest
import subprocess
import tempfile
import os


class TestIntegration(unittest.TestCase):
    def test_full_workflow(self):
        """Интеграционный тест полного цикла"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Создание тестового архива
            test_zip = os.path.join(tmpdir, 'test_lab.zip')
            with zipfile.ZipFile(test_zip, 'w') as zf:
                zf.writestr('lab.py', 'print("Lab output")')
                zf.writestr('lab.patch',
                            '--- a/lab.py\n+++ b/lab.py\n@@ -1 +1 @@\n-print("Lab output")\n+print("Patched output")')

            # Запуск полного цикла
            result = subprocess.run(
                ['./scripts/run.sh', '-l', 'test_lab', '-a', test_zip, '-t', '5'],
                capture_output=True,
                text=True
            )

            # Проверки
            self.assertIn('Lab setup completed', result.stdout)
            self.assertIn('Patched output', result.stdout)
            self.assertEqual(result.returncode, 0)