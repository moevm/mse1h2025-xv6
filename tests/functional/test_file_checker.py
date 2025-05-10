import pytest
import sys
import importlib
import os
import tempfile
import logging
from unittest.mock import patch

@pytest.fixture(autouse=True)
def mock_arguments():
    """Фиктивные аргументы для всех тестов"""
    with patch.object(sys, 'argv', ['file_checker.py', 'util', 'dummy.zip']):
        yield

@pytest.fixture
def file_checker():
    return importlib.reload(importlib.import_module('scripts.file_checker'))

@pytest.fixture
def test_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        user_dir = os.path.join(tmpdir, "user")
        os.makedirs(user_dir)

        # Valid C file
        with open(os.path.join(user_dir, "valid.c"), "w", encoding="utf-8") as f:
            f.write("/* Valid C file */")

        # File with non-UTF-8 encoding
        with open(os.path.join(user_dir, "invalid_enc.txt"), "w", encoding="cp1251") as f:
            f.write("Лорем ипсум")

        # Large file (2MB)
        with open(os.path.join(user_dir, "big.file"), "wb") as f:
            f.write(b"A" * 2 * 1024 * 1024)

        # File with invalid extension
        with open(os.path.join(user_dir, "invalid_ext.py"), "w", encoding="utf-8") as f:
            f.write("# Python file")

        yield tmpdir

def test_file_validation(file_checker, test_files):
    logger = logging.getLogger('FileChecker')
    logger.setLevel(logging.INFO)

    # Очистка обработчиков логов
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    logger.addHandler(logging.NullHandler())

    errors, dirs, files = file_checker.validate_files(
        test_files,
        ['.c', '.h', '.txt'],  # Допустимые расширения
        logger,
        max_size_mb=1  # Максимальный размер
    )

    assert dirs == 1, "Должна быть проверена 1 директория user"
    assert files == 4, "Должно быть проверено 4 файла"
    assert len(errors) == 4, f"Обнаружено {len(errors)} ошибок вместо ожидаемых 4"

    error_messages = [e.lower() for e in errors]
    assert any("invalid extension" in e and '.file' in e for e in error_messages), "Неверное расширение для big.file"
    assert any("exceeds the maximum size" in e for e in error_messages), "Не обнаружено превышение размера"
    assert any("not in 'utf-8' encoding" in e for e in error_messages), "Проблема с кодировкой"
    assert any("invalid extension" in e and '.py' in e for e in error_messages), "Неверное расширение для .py"
