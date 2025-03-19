import argparse
import os
import sys
import tempfile
import zipfile
import tarfile
import shutil
import subprocess
import logging
from pathlib import Path

try:
    import py7zr
except ImportError:
    py7zr = None

try:
    import rarfile
except ImportError:
    rarfile = None

# путь к папке scripts
script_dir = Path(__file__).resolve().parent

logs_dir = script_dir.parent / 'logs'
logs_dir.mkdir(parents=True, exist_ok=True)  #создаём папку logs, если нет

log_file = logs_dir / 'load.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),  #перезаписывать каждый запуск
        logging.StreamHandler(sys.stdout)
    ]
)
logging.info(f"Logging to {log_file}")

def extract_archive(archive_path, extract_to):
    logging.info(f"Extracting archive: {archive_path}")

    suffix = archive_path.suffix.lower()

    try:
        if suffix == '.zip':
            with zipfile.ZipFile(archive_path, 'r') as archive:
                archive.extractall(extract_to)

        elif suffix in ['.tar', '.gz', '.tgz', '.tar.gz']:
            with tarfile.open(archive_path, 'r:*') as archive:
                archive.extractall(extract_to)

        elif suffix == '.7z':
            if py7zr is None:
                logging.error("py7zr is not installed! Install it with: pip install py7zr")
                sys.exit(1)
            with py7zr.SevenZipFile(archive_path, mode='r') as archive:
                archive.extractall(path=extract_to)

        elif suffix == '.rar':
            if rarfile is None:
                logging.error("rarfile is not installed! Install it with: pip install rarfile")
                sys.exit(1)
            try:
                rf = rarfile.RarFile(archive_path)
                rf.extractall(extract_to)
            except rarfile.RarCannotExec as e:
                logging.error(f"rarfile error: {e}. Make sure unrar or bsdtar is installed.")
                sys.exit(1)

        else:
            logging.error("Unsupported archive format!")
            sys.exit(1)

        logging.info(f"Archive successfully extracted to {extract_to}")

    except Exception as e:
        logging.error(f"Error while extracting archive: {e}")
        sys.exit(1)

def find_patch_file(directory):
    logging.info(f"Searching for patch file in {directory}")

    for ext in ('*.patch', '*.diff'):
        files = list(Path(directory).rglob(ext))
        if files:
            patch_file = files[0]
            logging.info(f"Found patch file: {patch_file}")
            return patch_file

    logging.warning("No patch file found!")
    return None

def apply_patch(patch_file, target_dir):
    logging.info(f"Applying patch {patch_file} to {target_dir}")

    try:
        cmd = ['patch', '-p1', '-i', str(patch_file)]
        result = subprocess.run(cmd, cwd=target_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            logging.info("Patch applied successfully using patch.")
            return True
        else:
            logging.warning(f"patch command failed: {result.stderr.strip()}")

        cmd = ['git', 'apply', str(patch_file)]
        result = subprocess.run(cmd, cwd=target_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            logging.info("Patch applied successfully using git apply.")
            return True
        else:
            logging.error(f"git apply failed: {result.stderr.strip()}")
            return False

    except Exception as e:
        logging.error(f"Error while applying patch: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Prepare lab work from archive and apply patch.')
    parser.add_argument('archive', help='Path to the lab archive (zip, rar, 7z, tar, tar.gz)')
    args = parser.parse_args()

    archive_path = Path(args.archive)

    if not archive_path.is_file():
        logging.error(f"File not found: {archive_path}")
        sys.exit(1)

    with tempfile.TemporaryDirectory() as temp_dir:
        logging.info(f"Temporary directory created: {temp_dir}")

        extract_archive(archive_path, temp_dir)

        patch_file = find_patch_file(temp_dir)

        if patch_file:
            success = apply_patch(patch_file, temp_dir)
            if not success:
                logging.error("Patch application failed. Exiting.")
                sys.exit(1)
        else:
            logging.warning("No patch found. Skipping patch application.")

        #папка lab_ready создаётся на одном уровне с scripts
        output_dir = script_dir.parent / 'lab_ready'
        logging.info(f"Output directory set to: {output_dir}")

        if output_dir.exists():
            shutil.rmtree(output_dir)
        shutil.copytree(temp_dir, output_dir)

        logging.info(f"Lab work successfully prepared in: {output_dir}")
        logging.info(f"Script directory: {script_dir}")
        logging.info(f"Lab ready directory: {output_dir}")

if __name__ == '__main__':
    main()

