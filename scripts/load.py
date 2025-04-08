import argparse
import os
import sys
import tempfile
import zipfile
import shutil
import subprocess
import logging
from pathlib import Path

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
    ]
)
logging.info(f"Logging to {log_file}")

def extract_archive(archive_path, extract_to):
    logging.info(f"Extracting archive: {archive_path}")

    suffix = archive_path.suffix.lower()

    if suffix != '.zip':
        logging.error("Only .zip archives are supported!")
        sys.exit(1)

    try:
        with zipfile.ZipFile(archive_path, 'r') as archive:
            archive.extractall(extract_to)

        logging.info(f"Archive successfully extracted to {extract_to}")

    except zipfile.BadZipFile as e:
        logging.error(f"Bad zip file: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error while extracting archive: {e}")
        sys.exit(1)


def find_patch_file(directory):
    logging.info(f"Searching for patch file in {directory}")

    for ext in ('*.patch', '*.diff'):
        files = list(Path(directory).rglob(ext))
        if files:
            patch_file = files[0]
            if patch_file.stat().st_size == 0:
                logging.error(f"Patch file {patch_file} is empty!")
                sys.exit(1)
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
    parser = argparse.ArgumentParser(description='Prepare lab work from .zip archive and apply patch.')
    parser.add_argument('archive', help='Path to the lab archive (.zip only)')
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
        try:
            shutil.copytree(temp_dir, output_dir)
        except Exception as e:
            logging.error(f"Error copying files to output directory: {e}")
            sys.exit(1)

        logging.info(f"Lab work successfully prepared in: {output_dir}")

if __name__ == '__main__':
    main()


