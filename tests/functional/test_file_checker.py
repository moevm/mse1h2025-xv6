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
        with open(os.path.join(user_dir, "valid.c"), "w") as f:
            f.write("/* Valid */")

        # Non-UTF8 file
        with open(os.path.join(user_dir, "invalid.txt"), "wb") as f:
            f.write(b"\x80abc")

        # Large file
        with open(os.path.join(user_dir, "big.file"), "wb") as f:
            f.write(b"A" * 2*1024*1024)

        # Invalid extension
        with open(os.path.join(user_dir, "bad.py"), "w") as f:
            f.write("print('test')")

        yield tmpdir

def test_file_validation(test_files):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    errors, dirs, files = file_checker.validate_files(
        test_files,
        valid_extensions=['.c', '.h', '.txt'],
        logger=logger,
        max_size_mb=1
    )

    assert dirs == 1
    assert files == 4
    assert len(errors) == 4
    assert any("invalid extension '.file'" in e for e in errors)
    assert any("exceeds the maximum size" in e for e in errors)
    assert any("not in 'utf-8' encoding" in e for e in errors)
    assert any("invalid extension '.py'" in e for e in errors)
