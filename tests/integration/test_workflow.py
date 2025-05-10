import shutil
import pytest
import subprocess
from pathlib import Path
import tempfile
import zipfile
import json
import logging
import os
import stat
import time


@pytest.fixture
def setup_lab_environment():
    base_dir = Path(__file__).parent.parent.parent
    lab_ready = base_dir / "lab_ready"
    logs_dir = base_dir / "logs"

    def remove_readonly(func, path, _):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    if lab_ready.exists():
        shutil.rmtree(lab_ready, onerror=remove_readonly)
    if logs_dir.exists():
        shutil.rmtree(logs_dir, onerror=remove_readonly)

    logs_dir.mkdir(parents=True)

    yield base_dir

    for _ in range(3):
        try:
            shutil.rmtree(lab_ready, ignore_errors=True, onerror=remove_readonly)
            shutil.rmtree(logs_dir, ignore_errors=True, onerror=remove_readonly)
            break
        except PermissionError:
            time.sleep(0.5)


@pytest.fixture
def create_test_zip():
    """Создаем тестовый архив с правильной структурой"""
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = Path(tmpdir) / "test_lab.zip"

        patch_content = b"""--- a/Makefile
+++ b/Makefile
@@ -182,6 +182,7 @@ UPROGS=\\
 	$U/_usertests\\
 	$U/_grind\\
 	$U/_wc\\
+	$U/_sleep\\

 fs.img: mkfs/mkfs README $(UPROGS)
 	mkfs/mkfs fs.img README $(UPROGS)
"""
        with zipfile.ZipFile(zip_path, 'w') as z:
            z.writestr("lab-util.patch", patch_content)

            z.writestr("src/sleep.c",
                       b"#include \"kernel/types.h\"\n#include \"user/user.h\"\n\nint main() { sleep(1); exit(0); }")

        print("\n=== TEST ARCHIVE CONTENTS ===")
        with zipfile.ZipFile(zip_path, 'r') as z:
            for file in z.namelist():
                print(f" - {file}")

        yield zip_path


def test_full_workflow(setup_lab_environment, create_test_zip):
    base_dir = setup_lab_environment
    scripts_dir = base_dir / "scripts"
    logs_dir = base_dir / "logs"

    xv6_dir = base_dir / "lab_ready" / "xv6-labs-2024"
    xv6_dir.mkdir(parents=True)

    subprocess.run(["git", "init"], cwd=xv6_dir, check=True)
    subprocess.run(["git", "remote", "add", "origin", "git://g.csail.mit.edu/xv6-labs-2024"],
                   cwd=xv6_dir, check=True)

    makefile_content = """UPROGS=\\
	$U/_cat\\
	$U/_echo\\
	$U/_forktest\\
	$U/_grep\\
	$U/_init\\
	$U/_kill\\
	$U/_ln\\
	$U/_ls\\
	$U/_mkdir\\
	$U/_rm\\
	$U/_sh\\
	$U/_stressfs\\
	$U/_usertests\\
	$U/_grind\\
	$U/_wc\\

fs.img: mkfs/mkfs README $(UPROGS)
	mkfs/mkfs fs.img README $(UPROGS)
"""
    with open(xv6_dir / "Makefile", "w") as f:
        f.write(makefile_content)

    subprocess.run(["git", "add", "Makefile"], cwd=xv6_dir, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=xv6_dir, check=True)
    subprocess.run(["git", "checkout", "-b", "util"], cwd=xv6_dir, check=True)

    load_cmd = [
        "python",
        str(scripts_dir / "load.py"),
        "util",
        str(create_test_zip)
    ]

    print(f"\nRunning command: {' '.join(load_cmd)}")

    load_result = subprocess.run(
        load_cmd,
        cwd=base_dir,
        capture_output=True,
        text=True,
        timeout=60
    )

    print("\n=== LOAD.PY OUTPUT ===")
    print("STDOUT:", load_result.stdout)
    print("STDERR:", load_result.stderr)
    print("RETURNCODE:", load_result.returncode)

    if load_result.returncode != 0:
        load_log_path = logs_dir / "load.log"
        if load_log_path.exists():
            print("\n=== LOAD.LOG CONTENTS ===")
            with open(load_log_path) as f:
                print(f.read())

    assert load_result.returncode == 0, (
        f"load.py failed with return code {load_result.returncode}\n"
        f"Command: {' '.join(load_cmd)}\n"
        f"STDOUT: {load_result.stdout}\n"
        f"STDERR: {load_result.stderr}"
    )

    with open(xv6_dir / "Makefile") as f:
        content = f.read()
    assert "$U/_sleep\\" in content, "Patch not applied correctly - sleep not added to UPROGS"

    checker_result = subprocess.run(
        ["python", str(scripts_dir / "file_checker.py")],
        cwd=base_dir,
        capture_output=True,
        text=True,
        timeout=30
    )

    print("\n=== FILE_CHECKER.PY OUTPUT ===")
    print("STDOUT:", checker_result.stdout)
    print("STDERR:", checker_result.stderr)

    assert checker_result.returncode == 0, "file_checker.py failed"


    report_result = subprocess.run(
        ["python", str(scripts_dir / "generate_report.py"), "test_report"],
        cwd=base_dir,
        capture_output=True,
        text=True
    )

    print("\n=== GENERATE_REPORT.PY OUTPUT ===")
    print("STDOUT:", report_result.stdout)
    print("STDERR:", report_result.stderr)

    assert report_result.returncode == 0, "generate_report.py failed"

    report_path = base_dir / "logs" / "test_report.json"
    assert report_path.exists(), "Report file not found"

    with open(report_path) as f:
        report = json.load(f)

    assert len(report) > 0, "Report is empty"
    assert any("Logging started" in entry["message"] for entry in report), "No log entries found"
