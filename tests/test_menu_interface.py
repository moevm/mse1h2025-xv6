import subprocess
import os
from pathlib import Path


def test_menu_interface():
    project_root = Path(__file__).parent.parent
    load_script = project_root / "scripts" / "load.py"

    result = subprocess.run(
        ["python", str(load_script), "--help"],
        capture_output=True,
        text=True,
        encoding="utf-8"
    )

    assert result.returncode == 0, (
        f"Ошибка выполнения команды. Код: {result.returncode}\n"
        f"Stderr: {result.stderr}\n"
        f"Stdout: {result.stdout}"
    )

    assert "usage: load.py" in result.stdout
    assert "Prepare lab work from archive and apply patch." in result.stdout
    assert "positional arguments:" in result.stdout
    assert "archive" in result.stdout
    assert "Path to the lab archive (zip, rar, 7z, tar, tar.gz)" in result.stdout