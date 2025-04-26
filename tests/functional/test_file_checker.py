import pytest
from scripts import file_checker
import os
import tempfile
import logging


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

        # Large file (2MB, exceeds 1MB limit) with invalid extension
        with open(os.path.join(user_dir, "big.file"), "wb") as f:
            f.write(b"A" * 2 * 1024 * 1024)

        # File with invalid extension but small size
        with open(os.path.join(user_dir, "invalid_ext.py"), "w", encoding="utf-8") as f:
            f.write("# Python file")

        yield tmpdir


def test_file_validation(test_files):
    logger = logging.getLogger('FileChecker')
    logger.setLevel(logging.INFO)

    # Clear any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Add a null handler to avoid output during tests
    logger.addHandler(logging.NullHandler())

    errors, dirs, files = file_checker.validate_files(
        test_files,
        ['.c', '.h', '.txt'],  # Valid extensions
        logger,
        max_size_mb=1  # Max size 1MB
    )

    # Debug output
    print(f"Found errors: {errors}")
    print(f"Directories checked: {dirs}")
    print(f"Files checked: {files}")

    assert dirs == 1, "Should find 1 user directory"
    assert files == 4, "Should check 4 files"
    assert len(errors) == 4, f"Should detect 4 errors (got: {errors})"

    error_messages = [e.lower() for e in errors]
    assert any("invalid extension" in e and '.file' in e for e in
               error_messages), "Should detect invalid extension for big.file"
    assert any("exceeds the maximum size" in e for e in error_messages), "Should detect large file"
    assert any("not in 'utf-8' encoding" in e for e in error_messages), "Should detect encoding issue"
    assert any(
        "invalid extension" in e and '.py' in e for e in error_messages), "Should detect invalid extension for .py"