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

        with open(os.path.join(user_dir, "valid.c"), "w", encoding="utf-8") as f:
            f.write("/* Valid C file */")

        with open(os.path.join(user_dir, "invalid_enc.txt"), "w", encoding="cp1251") as f:
            f.write("Лорем ипсум")

        with open(os.path.join(user_dir, "big.file"), "w") as f:
            f.write("A" * 2 * 1024 * 1024)

        yield tmpdir


def test_file_validation(test_files):
    logger = logging.getLogger('FileChecker')
    errors, dirs, files = file_checker.validate_files(
        test_files,
        ['.c', '.h', '.txt'],
        logger,
        max_size_mb=1
    )

    assert dirs == 1, "Should find 1 user directory"
    assert files == 3, "Should check 3 files"
    assert len(errors) == 2, "Should detect 2 errors"
    assert any("invalid extension" in e for e in errors)
    assert any("exceeds the maximum size" in e for e in errors)