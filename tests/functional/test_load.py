import pytest
from pathlib import Path
import zipfile
import subprocess
import shutil
import os


def test_patch_application(tmp_path):
    project_root = Path(__file__).resolve().parent.parent.parent
    scripts_dir = project_root / "scripts"

    test_project_root = tmp_path / "project"
    test_scripts_dir = test_project_root / "scripts"
    test_lab_ready_dir = test_project_root / "lab_ready"
    test_lab_ready_dir.mkdir(parents=True)
    test_scripts_dir.mkdir(parents=True)

    shutil.copy(
        scripts_dir / "load.py",
        test_scripts_dir / "load.py"
    )

    zip_path = tmp_path / "test.zip"
    with zipfile.ZipFile(zip_path, 'w') as z:
        patch_content = b"""--- a/Makefile
+++ b/Makefile
@@ -150,6 +150,7 @@ UPROGS=\\
 	$U/_grind\\
 	$U/_wc\\
 	$U/_zombie\\
+	$U/_sleep\\

 fs.img: mkfs/mkfs README $(UPROGS)
 	mkfs/mkfs fs.img README $(UPROGS)
"""
        z.writestr("sleep.patch", patch_content)

    xv6_dir = test_lab_ready_dir / "xv6-labs-2024"
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
	$U/_zombie\\

fs.img: mkfs/mkfs README $(UPROGS)
	mkfs/mkfs fs.img README $(UPROGS)
"""
    with open(xv6_dir / "Makefile", "w") as f:
        f.write(makefile_content)

    subprocess.run(["git", "add", "Makefile"], cwd=xv6_dir, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=xv6_dir, check=True)

    subprocess.run(["git", "checkout", "-b", "util"], cwd=xv6_dir, check=True)

    result = subprocess.run(
        [
            "python",
            str(test_scripts_dir / "load.py"),
            "util",  # lab_branch
            str(zip_path)
        ],
        cwd=test_project_root,
        capture_output=True,
        text=True
    )

    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

    assert result.returncode == 0, (
        f"Load failed with return code {result.returncode}\n"
        f"STDOUT: {result.stdout}\n"
        f"STDERR: {result.stderr}"
    )

    with open(xv6_dir / "Makefile") as f:
        content = f.read()

    assert "$U/_sleep\\" in content, "Patch not applied correctly - sleep not added to UPROGS"