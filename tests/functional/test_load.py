import pytest
from pathlib import Path
import tempfile
import zipfile
import subprocess
import shutil


def test_patch_application(tmp_path):
    # Create test zip with patch and source file
    zip_path = tmp_path / "test.zip"
    with zipfile.ZipFile(zip_path, 'w') as z:
        z.writestr("test.patch", b"--- a/file.txt\n+++ b/file.txt\n@@ -1 +1 @@\n-original\n+modified")
        z.writestr("file.txt", b"original")

    # Run load.py
    result = subprocess.run(
        ["python", "scripts/load.py", str(zip_path)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Load failed: {result.stderr}"

    # Verify file
    output_dir = Path("lab_ready")
    assert (output_dir / "file.txt").exists()

    with open(output_dir / "file.txt") as f:
        content = f.read()
    assert "modified" in content, "Patch not applied correctly"

    # Cleanup
    shutil.rmtree(output_dir, ignore_errors=True)