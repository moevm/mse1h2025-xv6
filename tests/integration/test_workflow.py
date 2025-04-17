import shutil
import pytest
import subprocess
from pathlib import Path
import tempfile
import zipfile
import json
import logging


@pytest.fixture
def setup_lab_environment():
    base_dir = Path(__file__).parent.parent
    lab_ready = base_dir / "lab_ready"
    logs_dir = base_dir / "logs"

    if lab_ready.exists():
        shutil.rmtree(lab_ready)
    logs_dir.mkdir(exist_ok=True)

    yield base_dir

    shutil.rmtree(lab_ready, ignore_errors=True)
    shutil.rmtree(logs_dir, ignore_errors=True)


@pytest.fixture
def create_test_zip():
    """Creates a valid test zip archive with necessary structure"""
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = Path(tmpdir) / "valid_lab.zip"
        with zipfile.ZipFile(zip_path, 'w') as z:
            z.writestr("test.patch", b"--- a/test.txt\n+++ b/test.txt\n@@ -1 +1 @@\n-original\n+modified")
            z.writestr("src/valid.c", "// Valid C file".encode('utf-8'))
            z.writestr("src/valid.h", "// Valid header".encode('utf-8'))
        yield zip_path


def test_full_workflow(setup_lab_environment, create_test_zip):
    base_dir = setup_lab_environment

    # Test load.py
    load_result = subprocess.run(
        ["python", str(base_dir / "scripts/load.py"), str(create_test_zip)],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert load_result.returncode == 0, f"Load failed: {load_result.stderr}"
    assert (base_dir / "lab_ready/src/valid.c").exists()

    # Test file_checker.py
    checker_result = subprocess.run(
        ["python", str(base_dir / "scripts/file_checker.py")],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert checker_result.returncode == 0, f"Validation failed: {checker_result.stderr}"

    # Test run_tests.py
    test_result = subprocess.run(
        ["python", str(base_dir / "scripts/run_tests.py")],
        capture_output=True,
        text=True,
        timeout=300
    )
    assert test_result.returncode == 0, f"Tests failed: {test_result.stderr}"

    # Test generate_report.py
    report_result = subprocess.run(
        ["python", str(base_dir / "scripts/generate_report.py"), "report"],
        capture_output=True,
        text=True
    )
    assert report_result.returncode == 0, f"Report failed: {report_result.stderr}"

    report_path = base_dir / "logs/report.json"
    assert report_path.exists(), "Report file missing"

    # Validate report
    with open(report_path) as f:
        report = json.load(f)
    assert len(report) > 0, "Empty report"
    assert any("All files meet the requirements" in entry["message"] for entry in report)