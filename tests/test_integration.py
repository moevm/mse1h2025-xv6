import shutil
import pytest
import zipfile
import subprocess
import os
import sys
import logging
from pathlib import Path

@pytest.fixture
def valid_archive(tmp_path):
    archive_path = tmp_path / "valid.zip"
    test_dir = tmp_path / "test_project"
    test_dir.mkdir()

    original_file = test_dir / "file.c"
    original_file.write_text("Original content\n", newline='\n')

    patch_content = """--- a/file.c
+++ b/file.c
@@ -1 +1 @@
-Original content
+Patched content
"""
    patch_file = test_dir / "changes.patch"
    patch_file.write_text(patch_content, newline='\n')


    with zipfile.ZipFile(archive_path, 'w') as z:
        z.write(original_file, arcname="file.c")
        z.write(patch_file, arcname="changes.patch")

    return archive_path

@pytest.fixture
def corrupted_archive(tmp_path):
    archive_path = tmp_path / "corrupted.zip"
    archive_path.write_text("Invalid ZIP content")
    return archive_path

def test_integration(valid_archive, tmp_path):

    patch_path = shutil.which('patch')
    assert patch_path is not None, "Patch utility not found in PATH"
    print(f"\nUsing patch from: {patch_path}")


    script_path = Path(__file__).resolve().parent.parent / "scripts" / "load.py"
    print(f"Script path: {script_path}")
    assert script_path.exists(), f"Script {script_path} does not exist"


    env = os.environ.copy()
    git_bin = Path(patch_path).parent
    env["PATH"] = f"{git_bin}{os.pathsep}{env['PATH']}"


    result = subprocess.run(
        [sys.executable, str(script_path), str(valid_archive)],
        capture_output=True,
        text=True,
        cwd=script_path.parent.parent,
        env=env
    )


    assert result.returncode == 0, (
        f"Script failed with output:\n"
        f"STDOUT: {result.stdout}\n"
        f"STDERR: {result.stderr}"
    )


    lab_ready = script_path.parent.parent / "lab_ready"
    assert lab_ready.exists(), "lab_ready directory not created"


    patched_file = lab_ready / "file.c"
    assert patched_file.exists(), "Patched file not found"

    expected_content = "Patched content\n"
    actual_content = patched_file.read_text()
    assert actual_content == expected_content, (
        f"File content mismatch:\n"
        f"Expected: {repr(expected_content)}\n"
        f"Actual: {repr(actual_content)}"
    )


    log_file = script_path.parent.parent / "logs" / "load.log"
    assert log_file.exists(), "Log file not created"

    logs = log_file.read_text()
    assert "Archive successfully extracted" in logs
    assert "Found patch file" in logs
    assert "Patch applied successfully" in logs

def test_error_handling(corrupted_archive, tmp_path):
    script_path = Path(__file__).resolve().parent.parent / "scripts" / "load.py"
    assert script_path.exists(), f"Script {script_path} does not exist"

    result = subprocess.run(
        [sys.executable, str(script_path), str(corrupted_archive)],
        capture_output=True,
        text=True,
        cwd=script_path.parent.parent
    )

    assert result.returncode != 0, "Script should fail with corrupted archive"

    log_file = script_path.parent.parent / "logs" / "load.log"
    assert log_file.exists(), "Log file not created"

    logs = log_file.read_text()
    assert "Error while extracting archive" in logs

def test_no_patch_scenario(tmp_path):
    archive_path = tmp_path / "no_patch.zip"
    test_dir = tmp_path / "test_project"
    test_dir.mkdir()

    original_file = test_dir / "file.c"
    original_file.write_text("Original content\n", newline='\n')

    with zipfile.ZipFile(archive_path, 'w') as z:
        z.write(original_file, arcname="file.c")

    script_path = Path(__file__).resolve().parent.parent / "scripts" / "load.py"
    assert script_path.exists(), f"Script {script_path} does not exist"

    result = subprocess.run(
        [sys.executable, str(script_path), str(archive_path)],
        capture_output=True,
        text=True,
        cwd=script_path.parent.parent
    )

    assert result.returncode == 0, "Script failed without patch"

    log_file = script_path.parent.parent / "logs" / "load.log"
    logs = log_file.read_text()
    assert "No patch file found" in logs